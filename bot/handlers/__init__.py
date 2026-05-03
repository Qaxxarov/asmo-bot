"""Register all routers."""
from aiogram import Router
from .admin import router as admin_router
from .order import router as order_router
from .user import router as user_router

def get_root_router() -> Router:
    root = Router()
    root.include_router(admin_router)
    root.include_router(order_router)
    root.include_router(user_router)
    return root
