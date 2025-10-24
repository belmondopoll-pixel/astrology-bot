# services/stars_payment_service.py
import logging
from typing import Dict, Optional
from aiogram.types import LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from database import db

logger = logging.getLogger(__name__)

class StarsPaymentService:
    def __init__(self):
        self.service_prices = {
            "compatibility": 55,
            "weekly_horoscope": 333,
            "tarot": 888,
            "natal": 999
        }

    def get_invoice(self, service_type: str, user_data: Dict = None) -> Dict:
        """Создание инвойса для Telegram Stars"""
        service_info = {
            "compatibility": {
                "title": "💑 Анализ совместимости",
                "description": "Подробный анализ совместимости двух знаков зодиака"
            },
            "weekly_horoscope": {
                "title": "📅 Гороскоп на неделю", 
                "description": "Расширенный гороскоп на 7 дней с детальными прогнозами"
            },
            "tarot": {
                "title": "🃏 Расклад Таро",
                "description": "Профессиональный расклад карт Таро с интерпретацией"
            },
            "natal": {
                "title": "🌌 Натальная карта",
                "description": "Персональная натальная карта по дате рождения с анализом"
            }
        }
        
        info = service_info.get(service_type, {})
        price = self.service_prices.get(service_type, 0)
        
        # Создаем payload для идентификации заказа
        payload_parts = [service_type]
        if user_data:
            if user_data.get('zodiac_sign'):
                payload_parts.append(user_data['zodiac_sign'])
            if user_data.get('first_sign'):
                payload_parts.append(user_data['first_sign'])
            if user_data.get('second_sign'):
                payload_parts.append(user_data['second_sign'])
            if user_data.get('spread_type'):
                payload_parts.append(user_data['spread_type'])
        
        payload = "_".join(payload_parts)
        
        return {
            "title": info.get("title", "Услуга"),
            "description": info.get("description", ""),
            "payload": payload,
            "currency": "XTR",
            "prices": [LabeledPrice(label=info.get("title", "Услуга"), amount=price)],
            "start_parameter": service_type
        }

    async def process_successful_payment(self, user_id: int, payload: str, total_amount: int) -> bool:
        """Обработка успешного платежа"""
        try:
            # Парсим payload для определения типа услуги
            parts = payload.split("_")
            service_type = parts[0]
            
            # Логируем платеж
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payments (user_id, service_type, amount_stars, status)
                    VALUES (?, ?, ?, 'completed')
                ''', (user_id, service_type, total_amount))
                conn.commit()

            logger.info(f"✅ Успешный платеж: {user_id} -> {service_type} за {total_amount} Stars")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки платежа: {e}")
            return False

    def get_service_price(self, service_type: str) -> int:
        """Получить стоимость услуги"""
        return self.service_prices.get(service_type, 0)

stars_payment_service = StarsPaymentService()
