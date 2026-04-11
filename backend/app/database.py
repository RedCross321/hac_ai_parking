from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .core.config import settings

# Создание движка БД
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Только для SQLite
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """
    Dependency для получения сессии БД.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
