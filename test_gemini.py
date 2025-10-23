import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.gemini_service import GeminiService

async def test_gemini():
    """Тестируем работу Gemini"""
    try:
        print("🧪 Тестирование Gemini API...")
        
        service = GeminiService()
        print(f"✅ Модель инициализирована: {service.model_name}")
        
        # Тестовый запрос
        test_prompt = "Напиши приветственное сообщение для астрологического бота (2-3 предложения)"
        response = await service._make_request(test_prompt)
        
        print("✅ Gemini работает корректно!")
        print(f"📝 Ответ: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Gemini: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_gemini())