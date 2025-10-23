import logging
import sqlite3
from typing import Dict, Any, Optional
from database import db

logger = logging.getLogger(__name__)

class BalanceService:
    def __init__(self):
        self.init_db()

    def init_db(self):
        """Инициализация таблицы балансов"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_balance (
                        user_id INTEGER PRIMARY KEY,
                        balance INTEGER DEFAULT 0,
                        total_earned INTEGER DEFAULT 0,
                        total_spent INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка инициализации таблицы балансов: {e}")

    async def get_balance(self, user_id: int) -> int:
        """Получить баланс пользователя"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT balance FROM user_balance WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return result[0]
                else:
                    # Создаем запись для нового пользователя
                    await self.create_user_balance(user_id, 500)  # Начальный баланс
                    return 500
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            return 0

    async def create_user_balance(self, user_id: int, initial_balance: int = 500):
        """Создать запись баланса для пользователя"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_balance 
                    (user_id, balance, total_earned) 
                    VALUES (?, ?, ?)
                ''', (user_id, initial_balance, initial_balance))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка создания баланса: {e}")

    async def update_balance(self, user_id: int, amount: int, operation: str = "add") -> bool:
        """Обновить баланс пользователя"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                if operation == "add":
                    cursor.execute('''
                        UPDATE user_balance 
                        SET balance = balance + ?, 
                            total_earned = total_earned + ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (amount, amount, user_id))
                elif operation == "subtract":
                    cursor.execute('''
                        UPDATE user_balance 
                        SET balance = balance - ?,
                            total_spent = total_spent + ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND balance >= ?
                    ''', (amount, amount, user_id, amount))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Ошибка обновления баланса: {e}")
            return False

    async def can_afford(self, user_id: int, cost: int) -> bool:
        """Проверить, может ли пользователь позволить себе покупку"""
        balance = await self.get_balance(user_id)
        return balance >= cost

    async def get_balance_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику по балансу"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT balance, total_earned, total_spent 
                    FROM user_balance WHERE user_id = ?
                ''', (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'balance': result[0],
                        'total_earned': result[1],
                        'total_spent': result[2]
                    }
                else:
                    await self.create_user_balance(user_id)
                    return {
                        'balance': 500,
                        'total_earned': 500,
                        'total_spent': 0
                    }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {'balance': 0, 'total_earned': 0, 'total_spent': 0}

# Глобальный экземпляр сервиса
balance_service = BalanceService()