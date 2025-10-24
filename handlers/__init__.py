# handlers/__init__.py
from .user_handlers import router as user_router
from .paid_services import router as paid_router

# Создаем главный роутер который объединяет все
main_router = user_router
main_router.include_router(paid_router)

__all__ = ['main_router']