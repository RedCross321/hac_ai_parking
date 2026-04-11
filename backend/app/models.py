from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from .database import Base

class TestCamera(Base):
    """
    Камера в тестовом режиме
    """
    __tablename__ = "test_cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(50), default="unknown")  # ok, camera_unreachable, unknown
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    snapshots = relationship("TestSnapshot", back_populates="camera", cascade="all, delete-orphan")


class TestSnapshot(Base):
    """
    Снимок с камеры в тестовом режиме
    """
    __tablename__ = "test_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("test_cameras.id"), nullable=False)
    image_path = Column(String(500), nullable=False)
    free_count = Column(Integer, default=0)
    not_free_count = Column(Integer, default=0)
    partially_free_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    inference_status = Column(String(50), default="pending")  # pending, completed, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    camera = relationship("TestCamera", back_populates="snapshots")


class UserRequest(Base):
    """
    Логирование запросов пользователей
    """
    __tablename__ = "user_requests"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    ip_address = Column(String(50))
    request_data = Column(Text)
    response_status = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)