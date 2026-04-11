from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
# Импорты из наших модулей (убедись, что файлы созданы)
from app import crud, models, schemas, dependencies
from app.database import engine
from app import auth
from app.routers import captcha

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth" ,tags=["auth"])

# ========== ЭНДПОИНТЫ АВТОРИЗАЦИИ ==========
# Регистрация нового пользователя
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    # Проверяем, не занят ли email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # Проверяем, не занят ли username
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    # Создаём пользователя
    return crud.create_user(db=db, user=user)


# Логин - получение JWT токена
@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db)
):
    """
    POST /auth/login
    Принимает form-data с полями username и password
    Возвращает access_token
    """
    # Проверяем учетные данные
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаём токен
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Получение данных текущего пользователя (защищённый эндпоинт)
@router.get("/me", response_model=schemas.UserOut)
def read_auth_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user


# ========== ТВОИ БУДУЩИЕ ЭНДПОИНТЫ ДЛЯ PARKING ANALYZER ==========
# Здесь можешь добавлять свои эндпоинты для анализа парковок
# Например:
# @app.get("/parking/status")
# def get_parking_status(current_user: models.User = Depends(dependencies.get_current_user)):
#     return {"message": f"Parking data for {current_user.username}"}
