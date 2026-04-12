from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .models import User
from .database import engine, Base, get_db, SessionLocal
from .routers.test_mode import router as test_mode_router
from .routers.user import router as user_router
from .core.config import settings
from .routers import captcha, login, password_reset
from .services.camera_stream_service import scheduled_camera_update
from contextlib import asynccontextmanager
import asyncio
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


async def camera_update_task():
    """Фоновая задача для периодического обновления скриншотов камер."""
    # Даем время приложению полностью запуститься
    await asyncio.sleep(5)
    await scheduled_camera_update()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    Base.metadata.create_all(bind=engine)
    
    # Запускаем фоновые задачи
    cleanup_task_handle = asyncio.create_task(cleanup_task())
    camera_update_task_handle = asyncio.create_task(camera_update_task())
    
    yield
    
    # Отменяем задачи при остановке
    cleanup_task_handle.cancel()
    camera_update_task_handle.cancel()
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

app.include_router(auth_router)
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    """При запуске сервера проверяем состояние bootstrap"""
    try:
        db = next(get_db())
        admin_exists = db.query(User).filter(User.is_admin == True).first() is not None
        
        if not admin_exists:
            print("\n" + "="*60)
            print("🔐 ПЕРВЫЙ ЗАПУСК! НАСТРОЙКА АДМИНИСТРАТОРА")
            print("="*60)
            print("📌 Доступные эндпоинты для настройки:")
            print("   GET  http://localhost:8000/auth/bootstrap-token")
            print("   POST http://localhost:8000/auth/bootstrap-admin")
            print("\n⚠️  Эти эндпоинты будут отключены после создания первого админа!")
            print("="*60 + "\n")
        else:
            print("\n✅ Система готова к работе. Администратор уже существует.\n")
    except Exception as e:
        print(f"⚠️ Ошибка при проверке администратора: {e}")
        
app.include_router(login.router)
app.include_router(password_reset.router)
app.include_router(captcha.router)
app.include_router(test_mode_router)
app.include_router(user_router)


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
