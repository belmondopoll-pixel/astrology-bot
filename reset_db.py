import os
import sqlite3

def reset_database():
    """Пересоздает базу данных"""
    print("🔄 Пересоздание базы данных...")
    
    if os.path.exists('zodiac_bot.db'):
        os.remove('zodiac_bot.db')
        print("✅ Старая база данных удалена")
    
    # Импортируем и инициализируем новую базу
    from database import db
    print("✅ Новая база данных создана")
    
    # Проверяем таблицы
    conn = sqlite3.connect('zodiac_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✅ Создано таблиц: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    conn.close()

if __name__ == "__main__":
    reset_database()