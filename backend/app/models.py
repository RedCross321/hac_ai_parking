from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from .database import Base
import enum


class TripSessionStatus(str, enum.Enum):
    """Статус сессии поездки."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class BootstrapState(Base):
    __tablename__ = "bootstrap_state"
    
    id = Column(Integer, primary_key=True)
    is_used = Column(Boolean, default=False)
    bootstrap_token = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TokenBlackList(Base):
    """Модель черного списка токенов."""
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)


class TestCamera(Base):
    """
    Камера в тестовом режиме.
    """
    __tablename__ = "test_cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(50), default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    snapshots = relationship("TestSnapshot", back_populates="camera", cascade="all, delete-orphan")


class TestSnapshot(Base):
    """
    Снимок с камеры в тестовом режиме.
    """
    __tablename__ = "test_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("test_cameras.id"), nullable=False)
    image_path = Column(String(500), nullable=False)
    free_count = Column(Integer, default=0)
    not_free_count = Column(Integer, default=0)
    partially_free_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    inference_status = Column(String(50), default="pending")
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    camera = relationship("TestCamera", back_populates="snapshots")


class UserRequest(Base):
    """
    Логирование запросов пользователей.
    """
    __tablename__ = "user_requests"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    ip_address = Column(String(50))
    request_data = Column(Text)
    response_status = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class TripSession(Base):
    """
    Сессия поездки пользователя.
    """
    __tablename__ = "trip_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default=TripSessionStatus.ACTIVE.value)
    start_latitude = Column(Float)
    start_longitude = Column(Float)
    end_latitude = Column(Float)
    end_longitude = Column(Float)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    """
    Уведомления для пользователя.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trip_session_id = Column(Integer, ForeignKey("trip_sessions.id"), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(50), default="info")
    created_at = Column(DateTime, default=datetime.utcnow)
