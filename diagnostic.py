import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

async def diagnostic():
    """Диагностика всех систем"""
    print("🔧 Запуск диагностики...")
    
    # Проверка конфигурации
    try:
        from config import BOT_TOKEN, GEMINI_API_KEY
        print("✅ Конфигурация: OK")
        print(f"   BOT_TOKEN: {'***' + BOT_TOKEN[-4:] if BOT_TOKEN else 'НЕТ'}")
        print(f"   GEMINI_API_KEY: {'***' + GEMINI_API_KEY[-4:] if GEMINI_API_KEY else 'НЕТ'}")
    except Exception as e:
        print(f"❌ Конфигурация: {e}")
    
    # Проверка базы данных
    try:
        from database import db
        print("✅ База данных: OK")
    except Exception as e:
        print(f"❌ База данных: {e}")
    
    # Проверка Gemini
    try:
        from services.gemini_service import gemini_service
        if gemini_service.model_name != "none":
            print(f"✅ Gemini API: OK (модель: {gemini_service.model_name})")
        else:
            print("⚠️ Gemini API: Только локальная генерация")
    except Exception as e:
        print(f"❌ Gemini API: {e}")
    
    print("🎯 Диагностика завершена")

if __name__ == "__main__":
    asyncio.run(diagnostic())