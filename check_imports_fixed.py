import sys
import os
sys.path.append(os.path.dirname(__file__))

def check_all_imports():
    """Проверяем все критические импорты"""
    print("🔍 Проверка всех импортов...")
    
    imports_to_check = [
        ("typing", ["List", "Dict", "Tuple"]),
        ("aiogram", ["Router", "F"]),
        ("aiogram.types", ["Message", "CallbackQuery"]),
        ("aiogram.fsm.context", ["FSMContext"]),
        ("aiogram.fsm.state", ["State", "StatesGroup"]),
        ("database", ["db"]),
        ("keyboards", ["zodiac_keyboard", "tarot_spreads_keyboard"]),
        ("services.gemini_service", ["gemini_service"]),
        ("services.payment_service", ["payment_service"]),
        ("services.tarot_deck", ["tarot_deck"]),
        ("utils.message_utils", ["split_message"])
    ]
    
    all_ok = True
    
    for module_name, attributes in imports_to_check:
        try:
            module = __import__(module_name, fromlist=attributes)
            for attr in attributes:
                if hasattr(module, attr):
                    print(f"✅ {module_name}.{attr}: ОК")
                else:
                    print(f"❌ {module_name}.{attr}: НЕ НАЙДЕН")
                    all_ok = False
        except ImportError as e:
            print(f"❌ {module_name}: ОШИБКА ИМПОРТА - {e}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    success = check_all_imports()
    if success:
        print("\n🎉 Все импорты работают корректно!")
    else:
        print("\n💥 Обнаружены проблемы с импортами!")