from fastapi import APIRouter, Depends
from app import crud
from app.dependencies import get_current_user, get_db
from ..dependencies import oauth2_scheme
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    ):
    
    crud.add_token_to_blacklist(db, token)
    return {"message": "Token has been invalidated. You are logged out."}
    

