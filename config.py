import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ADMIN_ID = os.getenv('ADMIN_ID', '123456789')  # Ваш Telegram ID

# Проверяем обязательные переменные
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден в .env файле")
    print("💡 Получите токен у @BotFather и добавьте в .env:")
    print("BOT_TOKEN=ваш_токен_бота")
    
if not GEMINI_API_KEY:
    print("❌ ОШИБКА: GEMINI_API_KEY не найден в .env файле")
    print("💡 Получите API ключ на https://aistudio.google.com/ и добавьте в .env:")
    print("GEMINI_API_KEY=ваш_gemini_api_ключ")