from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.auth import router as auth_router
from app.database import get_db
from app.models import User

# создание нового объекта класса FastAPI
app = FastAPI(title="Parking Analyzer API")

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

# ПОДКЛЮЧАЕМ НАШИ АВТОРИЗАЦИОННЫЕ ЭНДПОИНТЫ
# Все эндпоинты из auth.py будут доступны с префиксом /auth
app.include_router(auth_router)

# СОЗДАЕМ ТАБЛИЦЫ В БАЗЕ ДАННЫХ ПРИ ЗАПУСКЕ
Base.metadata.create_all(bind=engine)

# декоратор, регистрирующий функцию ping как обработчик GET по пути /ping
@app.get("/ping")
async def ping():
    return {"status": "ok"}

# Добавим корневой эндпоинт для проверки работы API
@app.get("/")
async def root():
    return {"message": "Parking Analyzer API is running", "status": "healthy"}

# Добавим эндпоинт для проверки здоровья
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ПРОВЕРКА ПРИ ЗАПУСКЕ - есть ли уже администратор
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

# Для прямого запуска (опционально)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)