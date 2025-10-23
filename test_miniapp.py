import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

async def test_miniapp_integration():
    """Тест интеграции MiniApp"""
    print("🧪 Тестирование интеграции MiniApp...")
    
    try:
        # Проверка конфигурации
        from config import BOT_TOKEN
        print("✅ BOT_TOKEN: OK")
        
        # Проверка базы данных
        from database import db
        print("✅ База данных: OK")
        
        # Проверка сервиса MiniApp
        from services.miniapp_service import miniapp_service
        print("✅ MiniApp сервис: OK")
        
        # Тестовый запрос
        test_result = await miniapp_service.get_user_data(123456)
        print(f"✅ Тестовые данные пользователя: {test_result}")
        
        print("\n🎉 Все системы готовы к работе с MiniApp!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_miniapp_integration())