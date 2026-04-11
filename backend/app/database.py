from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()   
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
