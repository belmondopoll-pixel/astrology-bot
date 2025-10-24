import sqlite3
import logging
from datetime import datetime

class Database:
    def __init__(self, db_path='zodiac_bot.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER UNIQUE NOT NULL,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        zodiac_sign TEXT,
                        birth_date TEXT,
                        birth_time TEXT,
                        birth_place TEXT,
                        balance INTEGER DEFAULT 0,
                        subscription_type TEXT DEFAULT 'free',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица платежей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        service_type TEXT NOT NULL,
                        amount_stars INTEGER NOT NULL,
                        status TEXT DEFAULT 'completed',
                        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        payment_data TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                    )
                ''')
                
                # Таблица запросов (для статистики)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        service_type TEXT NOT NULL,
                        request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cost INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                    )
                ''')
                
                # Таблица истории операций
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                    )
                ''')
                
                conn.commit()
                logging.info("База данных успешно инициализирована")
                
        except sqlite3.Error as e:
            logging.error(f"Ошибка инициализации БД: {e}")

    def get_connection(self):
        """Получить соединение с БД"""
        return sqlite3.connect(self.db_path)

    def add_user(self, telegram_id, username, first_name, last_name):
        """Добавить пользователя с начальным балансом"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO users 
                    (telegram_id, username, first_name, last_name, balance) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (telegram_id, username, first_name, last_name, 100))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Ошибка добавления пользователя: {e}")
            return False

    def get_user(self, telegram_id):
        """Получить данные пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users WHERE telegram_id = ?
                ''', (telegram_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Ошибка получения пользователя: {e}")
            return None

    def get_user_balance(self, telegram_id):
        """Получить баланс пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT balance FROM users WHERE telegram_id = ?
                ''', (telegram_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Ошибка получения баланса: {e}")
            return 0

    def update_balance(self, telegram_id, amount):
        """Обновить баланс пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP
                    WHERE telegram_id = ?
                ''', (amount, telegram_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Ошибка обновления баланса: {e}")
            return False

    def log_request(self, telegram_id, service_type, cost=0):
        """Записать запрос в статистику"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO requests (user_id, service_type, cost) 
                    VALUES (?, ?, ?)
                ''', (telegram_id, service_type, cost))
                
                # Если услуга платная, списываем средства
                if cost > 0:
                    cursor.execute('''
                        UPDATE users SET balance = balance - ? 
                        WHERE telegram_id = ? AND balance >= ?
                    ''', (cost, telegram_id, cost))
                    
                    # Логируем транзакцию
                    cursor.execute('''
                        INSERT INTO transactions (user_id, type, amount, description)
                        VALUES (?, 'spend', ?, ?)
                    ''', (telegram_id, cost, f"Оплата услуги: {service_type}"))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Ошибка записи запроса: {e}")
            return False

    def get_user_requests(self, telegram_id, limit=10):
        """Получить историю запросов пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT service_type, request_date, cost 
                    FROM requests 
                    WHERE user_id = ? 
                    ORDER BY request_date DESC 
                    LIMIT ?
                ''', (telegram_id, limit))
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Ошибка получения истории запросов: {e}")
            return []

    def update_user_zodiac(self, telegram_id, zodiac_sign):
        """Обновить знак зодиака пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET zodiac_sign = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE telegram_id = ?
                ''', (zodiac_sign, telegram_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Ошибка обновления знака зодиака: {e}")
            return False

# Создаем глобальный экземпляр БД
db = Database()