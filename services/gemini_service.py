import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY не настроен")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Используем ТОЛЬКО модели, которые реально работают из нашего теста
        self.model_priority = [
            'gemini-2.0-flash-001',           # Основная - точно работает
            'gemini-2.0-flash',               # Альтернатива
            'gemini-2.0-flash-lite-001',      # Экономная версия
            'gemini-2.0-flash-exp',           # Экспериментальная
            'gemini-2.5-flash',               # Новая версия
            'gemini-2.5-flash-preview-05-20', # Премиум
        ]
        
        self.model = None
        self.model_name = None
        
        # Пробуем подключиться к моделям по порядку
        for model_name in self.model_priority:
            try:
                logger.info(f"🔄 Попытка инициализации модели: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                
                # Простой тестовый запрос
                test_response = self.model.generate_content(
                    "Тест", 
                    generation_config=genai.types.GenerationConfig(max_output_tokens=50)
                )
                
                self.model_name = model_name
                logger.info(f"✅ Успешно инициализирована модель: {model_name}")
                break
                
            except Exception as e:
                logger.warning(f"❌ Модель {model_name} не доступна: {e}")
                continue
        
        if self.model is None:
            logger.error("❌ Все модели Gemini недоступны")
            # Создаем заглушку чтобы бот мог работать без Gemini
            self.model = None
            self.model_name = "none"

    async def generate_horoscope(self, zodiac_sign: str, period: str = "сегодня") -> str:
        """Генерация гороскопа через Gemini"""
        if self.model is None:
            return await self._get_fallback_horoscope(zodiac_sign, period)
            
        prompt = f"""
        Напиши краткий астрологический прогноз для знака зодиака {zodiac_sign} на {period}.
        Будь позитивным и вдохновляющим. Объем: 100-150 слов.
        Формат:
        - Общее описание дня
        - Энергетика и настроение  
        - Совет дня
        - Что стоит учитывать
        
        Пиши на русском языке.
        """
        
        try:
            response = await self._make_request(prompt)
            return response
        except Exception as e:
            logger.error(f"Ошибка генерации гороскопа: {e}")
            return await self._get_fallback_horoscope(zodiac_sign, period)

    async def generate_compatibility(self, sign1: str, sign2: str) -> str:
        """Генерация анализа совместимости"""
        if self.model is None:
            from .fallback_service import fallback_service
            return fallback_service.generate_compatibility(sign1, sign2)
            
        prompt = f"""
        Проанализируй астрологическую совместимость между знаками {sign1} и {sign2}.
        
        Структура анализа:
        1. Общая характеристика пары
        2. Совместимость в любви и отношениях
        3. Совместимость в дружбе
        4. Совместимость в работе и бизнесе
        5. Сильные стороны союза
        6. Возможные challenges
        7. Рекомендации для гармоничных отношений
        
        Будь объективным, тактичным и профессиональным.
        Объем: 250-300 слов. На русском языке.
        """
        
        try:
            response = await self._make_request(prompt)
            return response
        except Exception as e:
            logger.error(f"Ошибка генерации совместимости: {e}")
            from .fallback_service import fallback_service
            return fallback_service.generate_compatibility(sign1, sign2)

    async def generate_weekly_horoscope(self, zodiac_sign: str, user_data: dict = None) -> str:
        """Генерация расширенного гороскопа на неделю"""
        if self.model is None:
            from .fallback_service import fallback_service
            return f"""
📅 Гороскоп на неделю для {zodiac_sign}

{fallback_service.generate_horoscope(zodiac_sign, "неделю")}

<em>Сервис AI временно недоступен. Это упрощенная версия гороскопа.</em>
"""
        
        user_context = ""
        if user_data:
            user_context = f"Дополнительная информация о пользователе: {user_data}"
        
        prompt = f"""
        Напиши подробный астрологический прогноз на предстоящую неделю для знака {zodiac_sign}.
        {user_context}
        
        Структура:
        - Общая характеристика недели
        - Подробный разбор по дням (понедельник - воскресенье):
          * Энергетика дня
          * Благоприятные действия
          * Возможные сложности
          * Совет дня
        - Итоговые рекомендации на неделю
        
        Будь конкретным и практичным. Объем: 400-500 слов. На русском языке.
        """
        
        try:
            response = await self._make_request(prompt)
            return response
        except Exception as e:
            logger.error(f"Ошибка генерации недельного гороскопа: {e}")
            from .fallback_service import fallback_service
            return f"""
📅 Гороскоп на неделю для {zodiac_sign}

{fallback_service.generate_horoscope(zodiac_sign, "неделю")}

<em>Сервис AI временно недоступен. Это упрощенная версия гороскопа.</em>
"""

    async def generate_natal_chart_interpretation(self, birth_data: dict) -> str:
        """Генерация интерпретации натальной карты"""
        if self.model is None:
            return "Извините, сервис генерации натальных карт временно недоступен."
            
        prompt = f"""
        Как профессиональный астролог, проанализируй натальную карту на основе данных:
        - Дата рождения: {birth_data.get('birth_date')}
        - Время рождения: {birth_data.get('birth_time')}
        - Место рождения: {birth_data.get('birth_place')}
        
        Структура анализа:
        1. Основные характеристики личности
        2. Сильные стороны и таланты
        3. Области для развития
        4. Эмоциональная природа
        5. Интеллектуальные способности
        6. Социальные аспекты
        7. Карьерный потенциал
        8. Рекомендации по личностному росту
        
        Будь глубоким, тактичным и вдохновляющим. Объем: 500-600 слов. На русском языке.
        """
        
        try:
            response = await self._make_request(prompt)
            return response
        except Exception as e:
            logger.error(f"Ошибка генерации натальной карты: {e}")
            return "Извините, не удалось сгенерировать натальную карту. Проверьте введенные данные."

    async def generate_tarot_reading(self, spread_type: str, question: str = None) -> str:
        """Генерация интерпретации расклада Таро"""
        if self.model is None:
            return "Извините, сервис раскладов Таро временно недоступен."
            
        spreads = {
            "celtic": "Кельтский крест - глубокий анализ текущей ситуации",
            "three": "Расклад на 3 карты - прошлое, настоящее, будущее",
            "four": "Расклад на 4 карты - ситуация, вызовы, совет, результат",
            "daily": "Карта дня - совет на сегодняшний день"
        }
        
        spread_description = spreads.get(spread_type, spread_type)
        
        prompt = f"""
        Как опытный таролог, интерпретируй расклад карт Таро: {spread_description}
        {"Вопрос пользователя: " + question if question else "Общий запрос на insight"}
        
        Структура интерпретации:
        - Общая энергетика расклада
        - Значение позиций карт в данном раскладе
        - Скрытые аспекты ситуации
        - Практические рекомендации
        - Потенциальные развития событий
        - Духовные уроки
        
        Будь мудрым, поддерживающим и избегай категоричных предсказаний.
        Объем: 300-400 слов. На русском языке.
        """
        
        try:
            response = await self._make_request(prompt)
            return response
        except Exception as e:
            logger.error(f"Ошибка генерации расклада Таро: {e}")
            return "Извините, не удалось получить расклад. Попробуйте позже."

    async def _make_request(self, prompt: str) -> str:
        """Базовый метод для запросов к Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    max_output_tokens=1500
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Ошибка запроса к Gemini: {e}")
            raise

    async def _get_fallback_horoscope(self, zodiac_sign: str, period: str) -> str:
        """Запасной вариант гороскопа при ошибке API"""
        from .fallback_service import fallback_service
        return fallback_service.generate_horoscope(zodiac_sign, period)

    async def safe_generate_horoscope(self, zodiac_sign: str, period: str = "сегодня") -> str:
        """Безопасная генерация гороскопа с резервным вариантом"""
        try:
            return await self.generate_horoscope(zodiac_sign, period)
        except Exception as e:
            logger.error(f"Gemini недоступен, используем резервный сервис: {e}")
            from .fallback_service import fallback_service
            return fallback_service.generate_horoscope(zodiac_sign, period)

# Создаем глобальный экземпляр сервиса
gemini_service = GeminiService()