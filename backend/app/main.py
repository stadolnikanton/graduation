from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, upload, share


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", 
        "http://localhost:5500",
        "http://localhost:3000",
        "http://localhost:8080",
    ],  
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(share.router)

