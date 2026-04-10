import os
import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

class CaptchaConfigResponse(BaseModel):
    site_key: str

@router.get("/captcha-config", response_model=CaptchaConfigResponse)
async def get_captcha_config():

    site_key = os.getenv("YANDEX_SMARTCAPTCHA_SITE_KEY")
    
    if not site_key:
        raise HTTPException(status_code=500, detail="SmartCaptcha Site Key is not configured on server.")
    
    # передача клиентского ключа
    return CaptchaConfigResponse(site_key=site_key)

class CaptchaVerifyRequest(BaseModel):
    token: str

@router.post("/verify-captcha")
async def verify_captcha(captcha_request: CaptchaVerifyRequest, request: Request):

    server_key = os.getenv("YANDEX_SMARTCAPTCHA_SERVER_KEY")

    if not server_key:
        raise HTTPException(status_code=500, detail="SmartCaptcha Server Key is not configured on server.")
    
    token = captcha_request.token

    user_ip = request.client.host
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        user_ip = forwarded_for.split(",")[0].strip()

    validation_url = "https://smartcaptcha.yandexcloud.net/validate"

    params = {
        "secret": server_key,
        "token": token,
        "ip": user_ip,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(validation_url, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get("status") == "ok":
                return {"status": "success", "message": "Validation passed", "host": data.get("host")}
            else:
                raise HTTPException(status_code=400, detail=f"Validation failed: {data.get("message")}")
    except httpx.RequestError as ex:
        raise HTTPException(status_code=503, detail=f"Error connecting to SmartCaptcha service: {ex}")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {ex}")