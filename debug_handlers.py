import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

async def debug_handlers():
    """Отладочный скрипт для проверки обработчиков"""
    print("🐛 ОТЛАДКА ЗАГРУЗКИ ОБРАБОТЧИКОВ")
    print("=" * 50)
    
    try:
        # Пробуем импортировать модули по одному
        print("1. Импорт config...")
        from config import BOT_TOKEN, GEMINI_API_KEY
        print("   ✅ config загружен")
        
        print("2. Импорт database...")
        from database import db
        print("   ✅ database загружен")
        
        print("3. Импорт paid_services...")
        from handlers.paid_services import router as paid_router
        print("   ✅ paid_services загружен")
        print(f"   Количество обработчиков в paid_services: {len(paid_router.message.handlers) + len(paid_router.callback_query.handlers)}")
        
        print("4. Импорт user_handlers...")
        from handlers.user_handlers import router
        print("   ✅ user_handlers загружен")
        print(f"   Количество обработчиков в user_handlers: {len(router.message.handlers) + len(router.callback_query.handlers)}")
        
        # Проверяем конкретные обработчики
        print("\n📋 ЗАРЕГИСТРИРОВАННЫЕ ОБРАБОТЧИКИ:")
        
        print("   Сообщения:")
        for handler in router.message.handlers:
            if hasattr(handler.filters, 'text') and hasattr(handler.filters.text, 'value'):
                print(f"     - {handler.filters.text.value}")
        
        print("   Callback-запросы:")
        for handler in router.callback_query.handlers:
            if hasattr(handler.filters, 'data'):
                print(f"     - {handler.filters.data}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_handlers())
    if success:
        print("\n🎉 Все модули загружены корректно!")
    else:
        print("\n💥 Обнаружены проблемы с загрузкой модулей!")