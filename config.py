import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ADMIN_ID = os.getenv('ADMIN_ID', '123456789')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')  # Добавьте эту строку

# Проверяем обязательные переменные
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден в .env файле")
    
if not GEMINI_API_KEY:
    print("❌ ОШИБКА: GEMINI_API_KEY не найден в .env файле")
