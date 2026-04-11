from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud, models, schemas, auth, dependencies
from app.database import engine

# Создание таблиц в БД при запуске
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Parking Analyzer API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"status": "ok"}

# ========== АВТОРИЗАЦИЯ ==========

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
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

@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db)
):
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

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user

@app.get("/auth/me", response_model=schemas.UserOut)
def read_auth_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user

# ========== ВОССТАНОВЛЕНИЕ ПАРОЛЯ ==========

@app.post("/auth/forgot-password")
async def forgot_password(
    request: schemas.ForgotPasswordRequest,
    db: Session = Depends(dependencies.get_db)
):
    reset_token = crud.create_password_reset_token(db, request.email)
    
    if not reset_token:
        return {
            "message": "If the email exists in our system, you will receive a password reset link"
        }
    
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    
    return {
        "message": "Password reset instructions sent",
        "debug_reset_token": reset_token,
        "debug_reset_link": reset_link
    }

@app.post("/auth/reset-password")
async def reset_password(
    request: schemas.ResetPasswordRequest,
    db: Session = Depends(dependencies.get_db)
):
    success = crud.reset_password(db, request.token, request.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password has been reset successfully"}