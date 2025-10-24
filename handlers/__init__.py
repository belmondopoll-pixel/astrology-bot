# handlers/__init__.py
import logging
from aiogram import Router

from .user_handlers import router as user_router
from .paid_services import router as paid_router

logger = logging.getLogger(__name__)

# Создаем главный роутер
main_router = Router()

# Включаем роутеры в правильном порядке - сначала платные услуги
main_router.include_router(paid_router)
main_router.include_router(user_router)

logger.info("✅ Роутеры инициализированы: paid_services -> user_handlers")

__all__ = ['main_router']