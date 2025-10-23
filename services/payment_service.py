# services/payment_service.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import logging
from database import db
from services.balance_service import balance_service

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.service_prices = {
            "compatibility": 55,
            "weekly_horoscope": 333,
            "natal_chart": 999,
            "tarot_reading": 888
        }

    def get_service_price(self, service_type: str) -> int:
        """Получить стоимость услуги в звездах"""
        return self.service_prices.get(service_type, 0)

    async def check_user_balance(self, user_id: int) -> int:
        """Проверить баланс пользователя"""
        return await balance_service.get_balance(user_id)

    async def process_payment(self, user_id: int, service_type: str) -> bool:
        """Обработать платеж за услугу"""
        price = self.get_service_price(service_type)
        
        # УБИРАЕМ ДЕМО-РЕЖИМ ДЛЯ АДМИНИСТРАТОРА
        # Все пользователи платят, включая администратора
        if await balance_service.can_afford(user_id, price):
            # Списание средств
            if await balance_service.update_balance(user_id, price, "subtract"):
                logger.info(f"✅ Оплата прошла: пользователь {user_id} оплатил {service_type} за {price} звезд")
                
                # Записываем платеж в базу
                try:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO payments (user_id, service_type, amount_stars, status)
                            VALUES (?, ?, ?, 'completed')
                        ''', (user_id, service_type, price))
                        conn.commit()
                    return True
                except Exception as e:
                    logger.error(f"Ошибка записи платежа: {e}")
                    # Возвращаем средства при ошибке
                    await balance_service.update_balance(user_id, price, "add")
                    return False
        else:
            logger.warning(f"❌ Недостаточно средств: у пользователя {user_id} недостаточно звезд")
            return False

    async def add_funds(self, user_id: int, amount: int) -> bool:
        """Пополнить баланс пользователя"""
        try:
            if await balance_service.update_balance(user_id, amount, "add"):
                logger.info(f"✅ Баланс пополнен: пользователь {user_id} +{amount} звезд")
                
                # Записываем пополнение в историю
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO payments (user_id, service_type, amount_stars, status)
                        VALUES (?, 'deposit', ?, 'completed')
                    ''', (user_id, amount))
                    conn.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка пополнения баланса: {e}")
            return False

    async def create_invoice(self, user_id: int, service_type: str, description: str):
        """Создать счет для оплаты"""
        price = self.get_service_price(service_type)
        current_balance = await self.check_user_balance(user_id)
        
        # УБИРАЕМ УСЛОВИЕ ДЛЯ АДМИНИСТРАТОРА
        instructions = f"Для оплаты услуги '{description}' требуется {price} Telegram Stars.\n\nВаш текущий баланс: {current_balance} звезд."
        
        return {
            "service_type": service_type,
            "description": description,
            "price_stars": price,
            "current_balance": current_balance,
            "instructions": instructions
        }

payment_service = PaymentService()