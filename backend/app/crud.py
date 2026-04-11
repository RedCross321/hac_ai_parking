from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime, timedelta
import secrets
from typing import Optional
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


# Trip Monitoring CRUD Functions

def create_trip_session(db: Session, user_id: int, start_latitude: Optional[float] = None, start_longitude: Optional[float] = None):
    """
    Создать новую сессию поездки.

    Args:
        db: Сессия базы данных SQLAlchemy.
        user_id: ID пользователя.
        start_latitude: Начальная широта.
        start_longitude: Начальная долгота.

    Returns:
        Созданный объект TripSession.
    """
    trip_session = models.TripSession(
        user_id=user_id,
        start_latitude=start_latitude,
        start_longitude=start_longitude
    )
    db.add(trip_session)
    db.commit()
    db.refresh(trip_session)
    return trip_session


def get_trip_session(db: Session, trip_session_id: int):
    """
    Получить сессию поездки по ID.

    Args:
        db: Сессия базы данных SQLAlchemy.
        trip_session_id: ID сессии поездки.

    Returns:
        Объект TripSession или None, если не найдено.
    """
    return db.query(models.TripSession).filter(models.TripSession.id == trip_session_id).first()


def cancel_trip_session(db: Session, trip_session_id: int):
    """
    Отменить сессию поездки.

    Args:
        db: Сессия базы данных SQLAlchemy.
        trip_session_id: ID сессии поездки.

    Returns:
        Обновленный объект TripSession или None, если не найдено.
    """
    from datetime import datetime
    trip_session = get_trip_session(db, trip_session_id)
    if not trip_session:
        return None
    
    if trip_session.status != "active":
        return None
    
    trip_session.status = "cancelled"
    trip_session.cancelled_at = datetime.utcnow()
    trip_session.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(trip_session)
    return trip_session


def create_notification(db: Session, user_id: int, title: str, message: str, trip_session_id: Optional[int] = None, notification_type: str = "info"):
    """
    Создать уведомление для пользователя.

    Args:
        db: Сессия базы данных SQLAlchemy.
        user_id: ID пользователя.
        title: Заголовок уведомления.
        message: Текст уведомления.
        trip_session_id: ID сессии поездки (опционально).
        notification_type: Тип уведомления.

    Returns:
        Созданный объект Notification.
    """
    notification = models.Notification(
        user_id=user_id,
        trip_session_id=trip_session_id,
        title=title,
        message=message,
        notification_type=notification_type
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_unread_notifications(db: Session, user_id: int, limit: int = 50):
    """
    Получить непрочитанные уведомления пользователя.

    Args:
        db: Сессия базы данных SQLAlchemy.
        user_id: ID пользователя.
        limit: Максимальное количество уведомлений.

    Returns:
        Список объектов Notification.
    """
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).order_by(models.Notification.created_at.desc()).limit(limit).all()


def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    """
    Отметить уведомление как прочитанное.

    Args:
        db: Сессия базы данных SQLAlchemy.
        notification_id: ID уведомления.
        user_id: ID пользователя (для проверки прав).

    Returns:
        Обновленный объект Notification или None, если не найдено.
    """
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if not notification:
        return None
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_notifications_as_read(db: Session, user_id: int):
    """
    Отметить все уведомления пользователя как прочитанные.

    Args:
        db: Сессия базы данных SQLAlchemy.
        user_id: ID пользователя.

    Returns:
        Количество обновленных уведомлений.
    """
    result = db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return result
