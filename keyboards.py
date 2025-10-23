from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Единый URL для MiniApp - ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ URL
MINIAPP_URL = "https://inspiring-dodol-70b9e9.netlify.app"

def get_webapp_url() -> str:
    """Получение URL для MiniApp"""
    return MINIAPP_URL

def main_menu():
    """Главное меню бота с MiniApp"""
    keyboard = [
        [KeyboardButton(text="♈ Ежедневный гороскоп")],
        [KeyboardButton(text="💑 Совместимость (55 звезд)")],
        [KeyboardButton(text="📅 Гороскоп на неделю (333 звезды)")],
        [KeyboardButton(text="🌌 Натальная карта (999 звезд)")],
        [KeyboardButton(text="🃏 Расклад Таро (888 звезд)")],
        [
            KeyboardButton(text="💰 Мой баланс"),
            KeyboardButton(text="💎 Пополнить баланс")
        ],
        [KeyboardButton(text="📚 Общая информация")],
        [KeyboardButton(text="📱 Открыть MiniApp", web_app=WebAppInfo(url=get_webapp_url()))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def web_app_keyboard():
    """Клавиатура с кнопкой MiniApp"""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="📱 Открыть MiniApp",
                web_app=WebAppInfo(url=get_webapp_url())
            )
        ]],
        resize_keyboard=True
    )

def zodiac_keyboard(prefix="horoscope"):
    """Клавиатура выбора знака зодиака"""
    zodiac_signs = [
        ("Овен", "♈"), ("Телец", "♉"), ("Близнецы", "♊"),
        ("Рак", "♋"), ("Лев", "♌"), ("Дева", "♍"),
        ("Весы", "♎"), ("Скорпион", "♏"), ("Стрелец", "♐"),
        ("Козерог", "♑"), ("Водолей", "♒"), ("Рыбы", "♓")
    ]
    
    buttons = []
    row = []
    
    for sign, emoji in zodiac_signs:
        row.append(InlineKeyboardButton(
            text=f"{emoji} {sign}", 
            callback_data=f"{prefix}_{sign}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def tarot_spreads_keyboard():
    """Клавиатура выбора расклада Таро"""
    buttons = [
        [InlineKeyboardButton(text="🧿 Кельтский крест", callback_data="tarot_celtic")],
        [InlineKeyboardButton(text="🔮 На 3 карты", callback_data="tarot_three")],
        [InlineKeyboardButton(text="✨ На 4 карты", callback_data="tarot_four")],
        [InlineKeyboardButton(text="🌟 Карта дня", callback_data="tarot_daily")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)