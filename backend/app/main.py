from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers.test_mode import router as test_mode_router
from .core.config import settings
from .routers import captcha, login, password_reset
from contextlib import asynccontextmanager
import asyncio
from .database import SessionLocal
import crud


async def cleanup_task():
    """Фоновая задача для очистки истекших токенов."""
    while True:
        await asyncio.sleep(3600)
        db = SessionLocal()

        try:
            crud.cleanup_expired_token(db)
        finally:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    Base.metadata.create_all(bind=engine)
    task = asyncio.create_task(cleanup_task())
    yield
    task.cancel()
    print("[→] Завершение работы приложения")


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

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
app.include_router(test_mode_router)


@app.get("/ping")
async def ping():
    """Проверка доступности сервиса."""
    return {"status": "ok"}


@app.get("/health")
async def health():
    """
    Health check endpoint без загрузки модели.

    Returns:
        dict: Статус сервиса и имя приложения.
    """
    return {"status": "ok", "service": settings.APP_NAME}
