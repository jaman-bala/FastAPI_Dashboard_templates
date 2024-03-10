import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles

from backend.user.router.user import router as user_router
from backend.app.pages.api import router as index_router
from backend.app.admin.router import router as admin_router

app = FastAPI(
    title="Applications"
)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
api_router = APIRouter()

api_router.include_router(index_router, prefix="", tags=["index"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(admin_router, prefix="/dashboard", tags=["admin"])

app.include_router(api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
