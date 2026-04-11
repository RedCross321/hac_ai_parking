from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routes.test_mode import router as test_mode_router
from .core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("[✓] Таблицы БД созданы")
    yield
    # Shutdown
    print("[→] Завершение работы приложения")


# создание нового объекта класса FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# разрешенные пути
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

# Регистрация роутов
app.include_router(test_mode_router)

# декоратор, регестрирующий функцию ping как обработчик GET по пути /ping
@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/health")
async def health():
    """
    Health check endpoint без загрузки модели.
    """
    return {"status": "ok", "service": settings.APP_NAME}