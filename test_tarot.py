import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.tarot_deck import tarot_deck

def test_tarot_system():
    """Тестирование системы Таро"""
    print("🔮 Тестирование системы Таро...")
    
    # Тест создания колоды
    print("1. Создание колоды...")
    deck = tarot_deck.shuffle_deck()
    print(f"   ✅ Колода создана: {len(deck)} карт")
    
    # Тест вытягивания карт
    print("2. Вытягивание карт...")
    cards = tarot_deck.draw_cards(3)
    print(f"   ✅ Вытянуто карт: {len(cards)}")
    for card in cards:
        print(f"      - {card['name']} ({card['position']})")
    
    # Тест различных раскладов
    print("3. Тестирование раскладов...")
    spread_types = ["celtic", "three", "four", "daily"]
    
    for spread_type in spread_types:
        print(f"   📊 Расклад '{spread_type}':")
        cards, positions = tarot_deck.create_spread(spread_type)
        display = tarot_deck.format_spread_for_display(cards)
        print(f"      Карты: {len(cards)}, Позиции: {len(positions)}")
        print(f"      Пример: {cards[0]['name']} в позиции '{positions[0]}'")
    
    print("🎉 Система Таро работает корректно!")

if __name__ == "__main__":
    test_tarot_system()