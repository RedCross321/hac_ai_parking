from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime, timedelta
import secrets
from jose import jwt, JWTError
from .auth import SECRET_KEY, ALGORITHM


def get_user_by_username(db: Session, username: str):
    """
    Получить пользователя из базы данных по имени пользователя.

    Args:
        db: Сессия базы данных SQLAlchemy.
        username: Имя пользователя для поиска.

    Returns:
        Объект User или None, если пользователь не найден.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """
    Получить пользователя из базы данных по адресу электронной почты.

    Args:
        db: Сессия базы данных SQLAlchemy.
        email: Адрес электронной почты для поиска.

    Returns:
        Объект User или None, если пользователь не найден.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Создать нового пользователя в базе данных.

    Args:
        db: Сессия базы данных SQLAlchemy.
        user: Схема данных пользователя для создания.

    Returns:
        Созданный объект User.
    """
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
    """
    Проверить учетные данные пользователя.

    Args:
        db: Сессия базы данных SQLAlchemy.
        username: Имя пользователя.
        password: Пароль в открытом виде.

    Returns:
        Объект User при успешной аутентификации, иначе False.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user


def add_token_to_blacklist(db: Session, token: str):
    """
    Добавить токен в черный список.

    Args:
        db: Сессия базы данных SQLAlchemy.
        token: JWT токен для добавления в черный список.

    Returns:
        Созданная запись TokenBlackList.
    """
    db_blacklist = models.TokenBlackList(token=token)
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist


def is_token_blacklisted(db: Session, token: str):
    """
    Проверить, находится ли токен в черном списке.

    Args:
        db: Сессия базы данных SQLAlchemy.
        token: JWT токен для проверки.

    Returns:
        True, если токен в черном списке, иначе False.
    """
    return db.query(models.TokenBlackList).filter(models.TokenBlackList.token == token).first() is not None


def cleanup_expired_token(db: Session):
    """
    Очистить истекшие токены из черного списка.

    Удаляет токены, у которых истек срок действия или которые некорректны.

    Args:
        db: Сессия базы данных SQLAlchemy.
    """
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


def create_password_reset_token(db: Session, email: str):
    """
    Создать токен для сброса пароля.

    Args:
        db: Сессия базы данных SQLAlchemy.
        email: Адрес электронной почты пользователя.

    Returns:
        Строка токена сброса или None, если пользователь не найден.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None

    reset_token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)

    user.reset_token = reset_token
    user.reset_token_expires = expires
    db.commit()
    db.refresh(user)

    return reset_token


def verify_reset_token(db: Session, token: str):
    """
    Проверить токен сброса пароля.

    Args:
        db: Сессия базы данных SQLAlchemy.
        token: Токен сброса пароля.

    Returns:
        Объект User при успешной проверке, иначе None.
    """
    user = db.query(models.User).filter(
        models.User.reset_token == token,
        models.User.reset_token_expires > datetime.utcnow()
    ).first()
    return user


def reset_password(db: Session, token: str, new_password: str):
    """
    Сбросить пароль пользователя.

    Args:
        db: Сессия базы данных SQLAlchemy.
        token: Токен сброса пароля.
        new_password: Новый пароль пользователя.

    Returns:
        True при успешном сбросе, иначе False.
    """
    user = verify_reset_token(db, token)
    if not user:
        return False

    user.hashed_password = auth.get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return True
