# main.py
import asyncio
import logging
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

# main.py - добавьте после импортов
logger.info("🔄 Начинается инициализация бота...")

try:
    from config import BOT_TOKEN
    from database import db
    from handlers import main_router
    # from api.server import miniapp_api  # Временно закомментируем
    
    logger.info("✅ Все модули успешно импортированы")
    
except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    import traceback
    logger.error(f"❌ Traceback: {traceback.format_exc()}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from config import BOT_TOKEN
    from database import db
    # Импортируем единый главный роутер
    from handlers import main_router
    # from api.server import miniapp_api  # Временно закомментируем
except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    import traceback
    logger.error(f"❌ Traceback: {traceback.format_exc()}")
    sys.exit(1)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter

async def main():
    """Основная функция запуска бота"""
    if not BOT_TOKEN or BOT_TOKEN == "ваш_токен_бота":
        logger.error("❌ BOT_TOKEN не настроен! Проверьте файл .env")
        return

    try:
        # Инициализация бота
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        # Регистрируем ЕДИНЫЙ главный роутер
        dp.include_router(main_router)
        
        logger.info("✅ Бот инициализирован, запускаем поллинг...")
        
        # ВРЕМЕННО ЗАКОММЕНТИРУЕМ API СЕРВЕР
        # try:
        #     asyncio.create_task(miniapp_api.start())
        #     logger.info("✅ API сервер запущен на порту 8080")
        # except Exception as e:
        #     logger.warning(f"⚠️ API сервер не запустился: {e}")
        
        # Запуск бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    logger.info("🚀 Запуск бота...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")