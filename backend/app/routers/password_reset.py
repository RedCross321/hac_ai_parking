from app import crud, schemas, dependencies
from sqlalchemy.orm import Session
from fastapi import  HTTPException, Depends, status, APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# ========== ВОССТАНОВЛЕНИЕ ПАРОЛЯ ==========
@router.post("/forgot-password")
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

@router.post("/reset-password")
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