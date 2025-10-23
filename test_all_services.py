import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.gemini_service import gemini_service
from services.fallback_service import fallback_service
from services.payment_service import payment_service

async def test_all_services():
    """Тестируем все сервисы"""
    print("🧪 Комплексное тестирование сервисов...")
    
    # Тест Gemini
    print("\n1. Тестирование Gemini API...")
    try:
        horoscope = await gemini_service.safe_generate_horoscope("Овен")
        print(f"✅ Gemini работает: {len(horoscope)} символов")
        print(f"📝 Пример: {horoscope[:100]}...")
    except Exception as e:
        print(f"❌ Gemini ошибка: {e}")
    
    # Тест Fallback Service
    print("\n2. Тестирование резервного сервиса...")
    try:
        fallback_horoscope = fallback_service.generate_horoscope("Телец")
        print(f"✅ Fallback сервис работает: {len(fallback_horoscope)} символов")
        print(f"📝 Пример: {fallback_horoscope[:100]}...")
    except Exception as e:
        print(f"❌ Fallback ошибка: {e}")
    
    # Тест Payment Service
    print("\n3. Тестирование платежной системы...")
    try:
        price = payment_service.get_service_price("compatibility")
        print(f"✅ Платежная система работает")
        print(f"💰 Цена совместимости: {price} звезд")
        
        # Тестовый платеж
        test_user_id = 12345
        result = await payment_service.process_payment(test_user_id, "compatibility")
        print(f"💳 Тестовый платеж: {'✅ Успех' if result else '❌ Ошибка'}")
        
    except Exception as e:
        print(f"❌ Payment ошибка: {e}")
    
    print("\n🎯 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_all_services())