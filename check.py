import asyncio
import sqlite3
import google.generativeai as genai
import os
from dotenv import load_dotenv

async def full_check():
    print("🔧 ПОЛНАЯ ДИАГНОСТИКА СИСТЕМЫ")
    print("=" * 60)
    
    # 1. Проверка .env файла
    print("\n1. Проверка файла .env...")
    load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    if BOT_TOKEN and BOT_TOKEN != "ваш_токен_бота":
        print("✅ BOT_TOKEN: НАЙДЕН")
    else:
        print("❌ BOT_TOKEN: НЕ НАЙДЕН или не настроен")
        
    if GEMINI_API_KEY and GEMINI_API_KEY != "ваш_gemini_api_ключ":
        print("✅ GEMINI_API_KEY: НАЙДЕН")
    else:
        print("❌ GEMINI_API_KEY: НЕ НАЙДЕН или не настроен")
    
    # 2. Проверка базы данных
    print("\n2. Проверка базы данных...")
    try:
        conn = sqlite3.connect('zodiac_bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ База данных: OK ({len(tables)} таблиц)")
        for table in tables:
            print(f"   - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ База данных: {e}")
    
    # 3. Проверка Gemini
    print("\n3. Проверка Gemini API...")
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-001')
            response = model.generate_content("Напиши 'Тест успешен' на русском")
            print("✅ Gemini API: РАБОТАЕТ")
            print(f"   Ответ: {response.text}")
        except Exception as e:
            print(f"❌ Gemini API: {e}")
    else:
        print("⚠️ Gemini API: Пропуск (нет API ключа)")
    
    # 4. Проверка файловой структуры
    print("\n4. Проверка файловой структуры...")
    required_files = [
        'main.py', 'config.py', 'database.py', 'keyboards.py',
        'handlers/user_handlers.py', 'handlers/paid_services.py',
        'services/gemini_service.py', 'services/payment_service.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: НАЙДЕН")
        else:
            print(f"❌ {file}: ОТСУТСТВУЕТ")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n💥 Отсутствуют файлы: {len(missing_files)}")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print("✅ Все файлы на месте")
    
    print("\n" + "=" * 60)
    print("🎯 Диагностика завершена")

if __name__ == "__main__":
    asyncio.run(full_check())