from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .database import get_db
from .models import User, BootstrapState
from .schemas import BootstrapAdminRequest, BootstrapAdminResponse, TokenResponse
import secrets
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
import bcrypt

router = APIRouter(prefix="/auth", tags=["authentication"])

SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def check_if_admin_exists(db: Session) -> bool:
    """Проверяет, есть ли уже хоть один администратор"""
    return db.query(User).filter(User.is_admin == True).first() is not None

def get_or_create_bootstrap_state(db: Session) -> BootstrapState:
    """Получает или создает запись о состоянии bootstrap"""
    state = db.query(BootstrapState).first()
    if not state:
        state = BootstrapState()
        db.add(state)
        db.commit()
        db.refresh(state)
    return state

def generate_and_store_bootstrap_token(db: Session) -> str:
    """Генерирует новый bootstrap токен и сохраняет в БД"""
    state = get_or_create_bootstrap_state(db)
    
    # Генерируем новый токен
    new_token = secrets.token_urlsafe(32)
    state.bootstrap_token = new_token
    state.is_used = False
    db.commit()
    
    return new_token

# Эндпоинт для получения токена (только при первом запуске)
@router.get("/bootstrap-token", response_model=TokenResponse)
async def get_bootstrap_token(db: Session = Depends(get_db)):
    """
    Возвращает bootstrap токен для создания первого админа.
    Доступен только если в системе нет администраторов.
    """
    # Проверяем, есть ли уже админ
    if check_if_admin_exists(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap already completed. Admin exists."
        )
    
    # Генерируем новый токен
    token = generate_and_store_bootstrap_token(db)
    
    return TokenResponse(
        bootstrap_token=token,
        message="Save this token! You'll need it to create the first admin. It will be shown only once."
    )

# ОСНОВНОЙ ЭНДПОИНТ - создание первого админа
@router.post("/bootstrap-admin", response_model=BootstrapAdminResponse)
async def bootstrap_admin(
    request: BootstrapAdminRequest,
    x_bootstrap_token: Optional[str] = Header(None),  # Используем Header для получения из заголовка
    db: Session = Depends(get_db)
):
    """
    Создает первого администратора в системе.
    Требует валидный X-Bootstrap-Token заголовок.
    Работает только один раз!
    """
    
    # Проверяем наличие токена
    if not x_bootstrap_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Bootstrap-Token header is required"
        )
    
    # 1. Проверяем, нет ли уже админа
    if check_if_admin_exists(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create admin. Admin already exists in the system."
        )
    
    # 2. Проверяем, что пароли совпадают
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # 3. Проверяем сложность пароля
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # 4. Проверяем bootstrap токен
    state = get_or_create_bootstrap_state(db)
    
    if state.is_used:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap token already used"
        )
    
    if not state.bootstrap_token or state.bootstrap_token != x_bootstrap_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bootstrap token"
        )
    
    # 5. Проверяем, не занят ли email
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 6. ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ - создаем администратора!
    hashed_pw = hash_password(request.password)
    
    new_admin = User(
        email=request.email,
        hashed_password=hashed_pw,
        is_admin=True,
        is_active=True
    )
    
    db.add(new_admin)
    
    # 7. Деактивируем bootstrap токен
    state.is_used = True
    state.bootstrap_token = None  # Очищаем токен для безопасности
    
    db.commit()
    
    return BootstrapAdminResponse(
        message=f"Success! Administrator {request.email} has been created.",
        admin_email=request.email
    )

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
