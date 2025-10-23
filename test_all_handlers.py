import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

async def test_all_handlers():
    """Тестируем что все обработчики загружаются корректно"""
    print("🧪 Тестирование загрузки всех обработчиков...")
    
    try:
        from handlers.user_handlers import router
        from handlers.paid_services import router as paid_router
        
        # Проверяем что роутеры загружены
        print("✅ Основной роутер: ЗАГРУЖЕН")
        print("✅ Роутер платных услуг: ЗАГРУЖЕН")
        
        # Проверяем наличие основных обработчиков
        handlers_count = len(router.message.handlers) + len(router.callback_query.handlers)
        paid_handlers_count = len(paid_router.message.handlers) + len(paid_router.callback_query.handlers)
        
        print(f"📊 Основных обработчиков: {handlers_count}")
        print(f"📊 Обработчиков платных услуг: {paid_handlers_count}")
        
        # Проверяем конкретные обработчики
        handler_texts = []
        for handler in router.message.handlers:
            if hasattr(handler.filters, 'text'):
                handler_texts.append(handler.filters.text)
        
        print("\n🔍 Загруженные обработчики сообщений:")
        for text in handler_texts:
            if hasattr(text, 'value'):
                print(f"   - {text.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки обработчиков: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_all_handlers())
    if success:
        print("\n🎉 Все обработчики загружены корректно!")
    else:
        print("\n💥 Обнаружены проблемы с обработчиками!")