from fastapi import FastAPI
from api.routes import auth, upload


app = FastAPI()

app.include_router(auth.router)
app.include_router(upload.router)