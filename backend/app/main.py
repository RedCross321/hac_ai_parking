from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.routers import captcha
from app.routers import login


# Создание таблиц в БД при запуске


app = FastAPI()

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
app.include_router(captcha.router)

# декоратор, регестрирующий функцию ping как обработчик GET по пути /ping
@app.get("/ping")
async def ping():
    return {"status": "ok"}