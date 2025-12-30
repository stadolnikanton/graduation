from fastapi import FastAPI
from api.routes import auth, upload, share


app = FastAPI()

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(share.router)