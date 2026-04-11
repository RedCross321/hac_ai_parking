from sqlalchemy.orm import Session
from . import models, schemas, auth

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