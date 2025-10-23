import random
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class TarotDeck:
    def __init__(self):
        self.major_arcana = [
            # Старшие Арканы (22 карты)
            {"name": "Шут", "number": 0, "upright": "Начало, невинность, спонтанность", "reversed": "Безрассудство, риск, незрелость"},
            {"name": "Маг", "number": 1, "upright": "Воля, мастерство, концентрация", "reversed": "Манипуляция, слабая воля, обман"},
            {"name": "Верховная Жрица", "number": 2, "upright": "Интуиция, тайны, подсознание", "reversed": "Скрытые мотивы, подавленная интуиция"},
            {"name": "Императрица", "number": 3, "upright": "Плодородие, изобилие, природа", "reversed": "Зависимость, расточительство, инертность"},
            {"name": "Император", "number": 4, "upright": "Власть, структура, контроль", "reversed": "Тирания, жесткость, доминирование"},
            {"name": "Иерофант", "number": 5, "upright": "Традиция, духовность, обучение", "reversed": "Догматизм, нетерпимость, подавление"},
            {"name": "Влюбленные", "number": 6, "upright": "Любовь, гармония, выбор", "reversed": "Дисгармония, неверность, нерешительность"},
            {"name": "Колесница", "number": 7, "upright": "Победа, контроль, прогресс", "reversed": "Отсутствие направления, агрессия, застой"},
            {"name": "Сила", "number": 8, "upright": "Сила воли, мужество, сострадание", "reversed": "Слабость, неуверенность, жестокость"},
            {"name": "Отшельник", "number": 9, "upright": "Самоанализ, уединение, мудрость", "reversed": "Одиночество, изоляция, отказ от помощи"},
            {"name": "Колесо Фортуны", "number": 10, "upright": "Судьба, поворот, циклы", "reversed": "Неудача, сопротивление переменам, застой"},
            {"name": "Справедливость", "number": 11, "upright": "Правосудие, карма, равновесие", "reversed": "Несправедливость, безответственность, предвзятость"},
            {"name": "Повешенный", "number": 12, "upright": "Жертва, сдача, новая перспектива", "reversed": "Мученичество, застой, сопротивление"},
            {"name": "Смерть", "number": 13, "upright": "Преобразование, конец, возрождение", "reversed": "Сопротивление переменам, страх, застой"},
            {"name": "Умеренность", "number": 14, "upright": "Баланс, терпение, гармония", "reversed": "Дисбаланс, нетерпение, крайности"},
            {"name": "Дьявол", "number": 15, "upright": "Искушение, зависимость, материализм", "reversed": "Освобождение, преодоление, самоконтроль"},
            {"name": "Башня", "number": 16, "upright": "Внезапные изменения, откровение, разрушение", "reversed": "Сопротивление изменениям, отсрочка, избегание"},
            {"name": "Звезда", "number": 17, "upright": "Надежда, вдохновение, духовность", "reversed": "Отчаяние, пессимизм, потеря веры"},
            {"name": "Луна", "number": 18, "upright": "Иллюзия, страх, подсознание", "reversed": "Осознание, преодоление страха, ясность"},
            {"name": "Солнце", "number": 19, "upright": "Радость, успех, жизненная сила", "reversed": "Временные трудности, задержки, эго"},
            {"name": "Суд", "number": 20, "upright": "Возрождение, призыв, прощение", "reversed": "Сомнения, отказ от призыва, самокритика"},
            {"name": "Мир", "number": 21, "upright": "Завершение, единство, достижение", "reversed": "Незавершенность, застой, разобщенность"}
        ]
        
        self.minor_arcana = [
            # Младшие Арканы (56 карт)
            # Жезлы
            *[{"name": f"{num} Жезлов", "suit": "Жезлы", "number": num} for num in ["Туз", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Паж", "Рыцарь", "Королева", "Король"]],
            # Кубки
            *[{"name": f"{num} Кубков", "suit": "Кубки", "number": num} for num in ["Туз", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Паж", "Рыцарь", "Королева", "Король"]],
            # Мечи
            *[{"name": f"{num} Мечей", "suit": "Мечи", "number": num} for num in ["Туз", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Паж", "Рыцарь", "Королева", "Король"]],
            # Пентакли
            *[{"name": f"{num} Пентаклей", "suit": "Пентакли", "number": num} for num in ["Туз", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Паж", "Рыцарь", "Королева", "Король"]]
        ]
        
        # Добавляем базовые значения для младших арканов
        for card in self.minor_arcana:
            suit_meanings = {
                "Жезлы": {"upright": "энергия, творчество, действие", "reversed": "промедление, отсутствие вдохновения"},
                "Кубки": {"upright": "эмоции, отношения, интуиция", "reversed": "эмоциональные проблемы, конфликты"},
                "Мечи": {"upright": "интеллект, конфликт, правда", "reversed": "сложные решения, умственное напряжение"},
                "Пентакли": {"upright": "материальное, работа, стабильность", "reversed": "финансовые проблемы, нестабильность"}
            }
            
            suit = card["suit"]
            if suit in suit_meanings:
                card["upright"] = suit_meanings[suit]["upright"]
                card["reversed"] = suit_meanings[suit]["reversed"]
        
        # Объединяем колоду
        self.full_deck = self.major_arcana + self.minor_arcana
    
    def shuffle_deck(self) -> List[Dict]:
        """Тасование колоды и возврат перемешанной колоды"""
        shuffled = self.full_deck.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def draw_cards(self, count: int = 1) -> List[Dict]:
        """Вытягивание указанного количества карт из колоды"""
        deck = self.shuffle_deck()
        drawn_cards = []
        
        for i in range(count):
            if i < len(deck):
                card = deck[i].copy()  # Создаем копию карты
                # Определяем положение карты (прямое или перевернутое)
                card["position"] = random.choice(["upright", "reversed"])
                drawn_cards.append(card)
        
        return drawn_cards
    
    def get_card_meaning(self, card: Dict) -> str:
        """Получение значения карты в зависимости от положения"""
        if "upright" in card and "reversed" in card:
            if card["position"] == "upright":
                return card["upright"]
            else:
                return card["reversed"]
        else:
            # Запасное значение если нет специфичных значений
            suit_meanings = {
                "Жезлы": "энергия, творчество, действие",
                "Кубки": "эмоции, отношения, интуиция", 
                "Мечи": "интеллект, конфликт, правда",
                "Пентакли": "материальное, работа, стабильность"
            }
            
            base_meaning = suit_meanings.get(card.get("suit", ""), "влияние, изменение")
            
            if card["position"] == "upright":
                return f"Позитивное влияние: {base_meaning}"
            else:
                return f"Вызов или сложность: {base_meaning}"
    
    def create_spread(self, spread_type: str) -> Tuple[List[Dict], List[str]]:
        """Создание расклада определенного типа"""
        spread_definitions = {
            "celtic": {
                "count": 10,
                "positions": [
                    "Настоящая ситуация",
                    "Вызов или препятствие", 
                    "Бессознательные влияния",
                    "Прошлое, что уходит",
                    "Сознательные цели",
                    "Ближайшее будущее",
                    "Ваше отношение к ситуации",
                    "Влияние окружения",
                    "Надежды и страхи",
                    "Итог или результат"
                ]
            },
            "three": {
                "count": 3,
                "positions": [
                    "Прошлое",
                    "Настоящее", 
                    "Будущее"
                ]
            },
            "four": {
                "count": 4, 
                "positions": [
                    "Ситуация",
                    "Вызовы",
                    "Совет",
                    "Результат"
                ]
            },
            "daily": {
                "count": 1,
                "positions": [
                    "Совет дня"
                ]
            }
        }
        
        spread_info = spread_definitions.get(spread_type, spread_definitions["daily"])
        cards = self.draw_cards(spread_info["count"])
        
        return cards, spread_info["positions"]
    
    def format_spread_for_display(self, cards: List[Dict]) -> str:
        """Форматирование расклада для отображения пользователю"""
        result = "🎴 Ваш расклад:\n\n"
        
        for i, card in enumerate(cards):
            position = card.get("position_name", f"Позиция {i+1}")
            orientation = "🔼" if card["position"] == "upright" else "🔽"
            result += f"{orientation} <b>{position}:</b>\n"
            result += f"   🃏 {card['name']}\n"
            result += f"   📖 {self.get_card_meaning(card)}\n\n"
        
        return result

    def get_available_spreads(self) -> Dict[str, str]:
        """Возвращает доступные типы раскладов"""
        return {
            "daily": "Совет дня (1 карта)",
            "three": "Прошлое-Настоящее-Будущее (3 карты)", 
            "four": "Ситуация-Вызовы-Совет-Результат (4 карты)",
            "celtic": "Кельтский крест (10 карт)"
        }

# Создаем глобальный экземпляр колоды
tarot_deck = TarotDeck()