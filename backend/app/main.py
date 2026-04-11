from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import captcha
from app.routers import login
from app.routers import password_reset

from contextlib import asynccontextmanager
import asyncio
from app.database import SessionLocal
from app import crud

from app import crud
from app.database import engine


async def cleanup_task():
    while True:
        await asyncio.sleep(3600)
        db = SessionLocal()

        try:
            crud.cleanup_expired_token(db)
        finally:
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(cleanup_task())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)



origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

]

# разрешение фронту отправлять запросы на бэк

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login.router)
app.include_router(password_reset.router)
app.include_router(captcha.router)

# декоратор, регестрирующий функцию ping как обработчик GET по пути /ping
@app.get("/ping")
async def ping():
    return {"status": "ok"}


