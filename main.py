# main.py
import asyncio
import logging
import os
import sys

# НАСТРОЙКА ЛОГИРОВАНИЯ ДОЛЖНА БЫТЬ САМОЙ ПЕРВОЙ СТРОКОЙ КОДА
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# СОЗДАЕМ ЛОГГЕР СРАЗУ ПОСЛЕ НАСТРОЙКИ
logger = logging.getLogger(__name__)

def setup_environment():
    """Настройка окружения"""
    logger.info("🔄 Настройка окружения...")
    sys.path.append(os.path.dirname(__file__))
    logger.info(f"✅ Python path: {sys.path}")

def import_modules():
    """Импорт модулей с обработкой ошибок"""
    try:
        logger.info("🔄 Импорт модулей...")
        
        from config import BOT_TOKEN, GEMINI_API_KEY, ADMIN_ID
        from database import db
        from handlers import main_router
        
        logger.info("✅ Все модули успешно импортированы")
        return BOT_TOKEN, db, main_router
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта модулей: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        sys.exit(1)

async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск бота...")
    
    # Настройка окружения и импорт модулей
    setup_environment()
    BOT_TOKEN, db, main_router = import_modules()
    
    if not BOT_TOKEN or BOT_TOKEN == "ваш_токен_бота":
        logger.error("❌ BOT_TOKEN не настроен! Проверьте файл .env")
        return

    try:
        from aiogram import Bot, Dispatcher
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        
        # Инициализация бота
        logger.info("🔄 Инициализация бота...")
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        # Регистрируем роутер
        dp.include_router(main_router)
        
        logger.info("✅ Бот инициализирован")
        logger.info("🔄 Запуск поллинга...")
        
        # Запуск бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")