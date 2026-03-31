from fastapi import FastAPI
from .api.routes import router

app = FastAPI(title="SEO Analysis Agent")

app.include_router(router)
