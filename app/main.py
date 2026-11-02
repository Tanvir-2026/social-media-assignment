from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import auth_routes
from app.database import init_db
from app.routes import post_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create tables on startup
    yield


app = FastAPI(title="Social Media Backend", lifespan=lifespan)

app.include_router(auth_routes.router)
app.include_router(post_routes.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}