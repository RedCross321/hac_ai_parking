from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from typing import Optional

SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверить соответствие пароля хешу.

    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хеш пароля.

    Returns:
        True, если пароль совпадает, иначе False.
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """
    Получить хеш пароля.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Хеш пароля.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создать JWT токен доступа.

    Args:
        data: Данные для кодирования в токене.
        expires_delta: Время действия токена. Если не указано, используется значение по умолчанию (15 минут).

    Returns:
        Закодированный JWT токен.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt