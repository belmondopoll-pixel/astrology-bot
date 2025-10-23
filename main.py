import asyncio
import logging
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter

try:
    from config import BOT_TOKEN
    from database import db
    from handlers.user_handlers import router
    from api.server import miniapp_api  # Импортируем API
except ImportError as e:
    logging.error(f"Ошибка импорта: {e}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            if not BOT_TOKEN or BOT_TOKEN == "ваш_токен_бота":
                logger.error("❌ BOT_TOKEN не настроен! Проверьте файл .env")
                return
            
            # Инициализация бота
            bot = Bot(
                token=BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            dp = Dispatcher()
            
            # Регистрация роутеров
            dp.include_router(router)
            
            # Запуск API сервера
            asyncio.create_task(miniapp_api.start())
            logger.info("✅ API сервер запущен на порту 8080")
            
            # Запуск бота
            logger.info("✅ Бот запускается...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
            
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            logger.warning(f"⚠️ Превышены лимиты Telegram. Повтор через {retry_after} сек.")
            await asyncio.sleep(retry_after)
            retry_count += 1
            
        except TelegramNetworkError as e:
            retry_count += 1
            wait_time = 2 ** retry_count
            logger.warning(f"🌐 Сетевая ошибка. Попытка {retry_count}/{max_retries}. Ждем {wait_time} сек.: {e}")
            
            if retry_count < max_retries:
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"❌ Достигнут максимум попыток ({max_retries}). Бот остановлен.")
                break
                
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {e}")
            retry_count += 1
            wait_time = min(30, 5 * retry_count)
            logger.info(f"🔄 Перезапуск через {wait_time} сек. (попытка {retry_count}/{max_retries})")
            await asyncio.sleep(wait_time)
            
        finally:
            if 'bot' in locals():
                await bot.session.close()
                
    logger.error("❌ Бот не смог запуститься после нескольких попыток")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")