from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# создание нового объекта класса FastAPI
app = FastAPI(title="Parking Analyzer API")

# разрешенные пути
origins = [

    "http://localhost:5173",
    "http://127.0.0.1:5173",

] 

# разрешение фронту отправлять запросы на бэк
app.add_middleware(

    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

# декоратор, регестрирующий функцию ping как обработчик GET по пути /ping
@app.get("/ping")
async def ping():
    return {"status": "ok"}