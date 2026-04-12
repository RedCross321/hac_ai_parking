from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import crud, models, schemas, dependencies, auth
from ..database import engine
from ..routers import captcha

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    """
    Зарегистрировать нового пользователя.

    Args:
        user: Данные пользователя для регистрации.
        db: Сессия базы данных.

    Returns:
        Созданный объект пользователя.

    Raises:
        HTTPException: Если email или username уже заняты.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    return crud.create_user(db=db, user=user)


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db)
):
    """
    Аутентификация пользователя и получение JWT токена.

    Args:
        form_data: Форма с username и password.
        db: Сессия базы данных.

    Returns:
        access_token и token_type.

    Raises:
        HTTPException: Если учетные данные неверны.
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def read_auth_me(current_user: models.User = Depends(dependencies.get_current_user)):
    """
    Получить данные текущего аутентифицированного пользователя.

    Args:
        current_user: Текущий пользователь.

    Returns:
        Данные пользователя.
    """
    return current_user
