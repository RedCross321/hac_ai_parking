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


def add_token_to_blacklist(db: Session, token: str):
    db_blacklist = models.TokenBlackList(token=token)
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist

def is_token_blacklisted(db: Session, token: str):
    return db.query(models.TokenBlackList).filter(models.TokenBlackList.token == token).first() is not None

def cleanup_expired_token(db: Session):

    from jose import jwt, JWTError
    from datetime import datetime
    from app.auth import SECRET_KEY, ALGORITHM

    now = datetime.utcnow()
    expired_tokens = []

    all_tokens = db.query(models.TokenBlackList).all()

    for record in all_tokens:
        try:
            payload = jwt.decode(record.token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")

            if exp:
                exp_date = datetime.utcfromtimestamp(exp)

                if exp_date < now:
                    expired_tokens.append(record)
        except JWTError:
            expired_tokens.append(record)

    for record in expired_tokens:
        db.delete(record)

    if expired_tokens:
        db.commit()
        print(f"Cleaned up {len(expired_tokens)} expired tokens.")

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
