from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime, timedelta
import secrets

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user

# Новые функции для восстановления пароля
def create_password_reset_token(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Генерируем безопасный токен
    reset_token = secrets.token_urlsafe(32)
    # Токен действителен 1 час
    expires = datetime.utcnow() + timedelta(hours=1)
    
    user.reset_token = reset_token
    user.reset_token_expires = expires
    db.commit()
    db.refresh(user)
    
    return reset_token

def verify_reset_token(db: Session, token: str):
    user = db.query(models.User).filter(
        models.User.reset_token == token,
        models.User.reset_token_expires > datetime.utcnow()
    ).first()
    return user

def reset_password(db: Session, token: str, new_password: str):
    user = verify_reset_token(db, token)
    if not user:
        return False
    
    # Хешируем новый пароль
    user.hashed_password = auth.get_password_hash(new_password)
    # Очищаем токен сброса
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return True