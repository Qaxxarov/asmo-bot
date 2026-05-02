from aiogram import Router

from .user import router as user_router
from .order import router as order_router
from .admin import router as admin_router


def get_root_router() -> Router:
    root = Router()
    # Order matters: admin first, then order FSM, then user fallback
    root.include_router(admin_router)
    root.include_router(order_router)
    root.include_router(user_router)
    return root
