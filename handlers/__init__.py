# handlers/__init__.py
from .user_handlers import router
from .paid_services import router as paid_router

# Объединяем все роутеры
__all__ = ['router', 'paid_router']