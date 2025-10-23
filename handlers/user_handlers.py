from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, WebAppData, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
import logging

from database import db
from keyboards import main_menu, zodiac_keyboard, web_app_keyboard, get_webapp_url
from services.gemini_service import gemini_service
from services.miniapp_service import miniapp_service
from services.balance_service import balance_service
from services.payment_service import payment_service

# Импортируем обработчики платных услуг
from .paid_services import router as paid_router

router = Router()
# Включаем роутер платных услуг
router.include_router(paid_router)

logger = logging.getLogger(__name__)

class UserStates(StatesGroup):
    waiting_for_zodiac = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    
    # Добавляем пользователя в БД
    db.add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    welcome_text = """
🌟 <b>Добро пожаловать в АстроБот!</b> 🌟

Я ваш личный астрологический помощник. Вот что я умею:

<b>Бесплатные услуги:</b>
♈ Ежедневный гороскоп
📚 Общая информация об астрологии

<b>Платные услуги (Telegram Stars):</b>
💑 Совместимость по знакам зодиака - 50 звёзд
📅 Расширенный гороскоп на неделю - 100 звёзд  
🌌 Натальная карта с интерпретацией - 200 звёзд
🃏 Расклад карт Таро - 80 звёзд

📱 <b>Новое!</b> Теперь доступно удобное MiniApp с красивым интерфейсом!
    """
    
    await message.answer(welcome_text, reply_markup=main_menu())

@router.message(F.text == "📱 Открыть MiniApp")
async def open_miniapp_handler(message: Message):
    """Обработчик открытия MiniApp"""
    
    await message.answer(
        "🚀 <b>Открытие MiniApp...</b>\n\n"
        "Если MiniApp не открывается автоматически, "
        "нажмите кнопку ниже:",
        reply_markup=web_app_keyboard()
    )

@router.message(F.text == "♈ Ежедневный гороскоп")
async def daily_horoscope_handler(message: Message, state: FSMContext):
    """Обработчик ежедневного гороскопа"""
    
    # Логируем запрос
    db.log_request(message.from_user.id, "daily_horoscope")
    
    await message.answer(
        "Выберите ваш знак зодиака:",
        reply_markup=zodiac_keyboard("horoscope")
    )

@router.callback_query(F.data.startswith("horoscope_"))
async def process_zodiac_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора знака зодиака"""
    
    zodiac_sign = callback.data.split("_")[1]
    
    # Сохраняем знак зодиака пользователя
    db.update_user_zodiac(callback.from_user.id, zodiac_sign)
    
    # Показываем "в процессе" сообщение
    processing_msg = await callback.message.edit_text(
        f"♈ Генерирую гороскоп для {zodiac_sign}...\n\n<em>Это может занять несколько секунд</em>"
    )
    
    try:
        # Генерируем гороскоп через Gemini
        horoscope_text = await gemini_service.safe_generate_horoscope(zodiac_sign)
        
        final_text = f"♈ <b>Гороскоп для {zodiac_sign}</b>\n\n{horoscope_text}"
        
        await callback.message.edit_text(final_text)
        
    except Exception as e:
        error_text = f"""
♈ <b>Гороскоп для {zodiac_sign}</b>

К сожалению, произошла ошибка при генерации гороскопа. 
Попробуйте еще раз через несколько минут.

<em>Ошибка: {str(e)}</em>
        """
        await callback.message.edit_text(error_text)
    
    await callback.answer()

@router.message(F.text == "📚 Общая информация")
async def general_info_handler(message: Message):
    """Обработчик общей информации"""
    
    info_text = """
<b>📚 Общая информация об астрологии</b>

<b>Астрология</b> - это древняя система знаний, изучающая влияние небесных тел на жизнь человека.

<b>Натальная карта</b> - это индивидуальная карта расположения планет в момент вашего рождения. Она показывает:
• Ваши врожденные качества
• Сильные и слабые стороны
• Потенциал развития

<b>Карты Таро</b> - система символов, используемая для гадания и самопознания. Популярные расклады:
• Кельтский крест - глубокий анализ ситуации
• Расклад на 3 карты - прошлое, настоящее, будущее
• Карта дня - совет на текущий день

Для получения подробной информации выберите соответствующую услугу в меню.
    """
    
    await message.answer(info_text)

@router.message(Command("app"))
async def cmd_app(message: Message):
    """Открыть MiniApp через команду"""
    await message.answer(
        f"📱 <b>MiniApp для АстроБота</b>\n\n"
        f"URL: {get_webapp_url()}\n\n"
        "Нажмите кнопку '📱 Открыть MiniApp' в меню "
        "или используйте кнопку ниже:",
        reply_markup=web_app_keyboard()
    )

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Обработка данных из MiniApp"""
    try:
        data = json.loads(message.web_app_data.data)
        service_type = data.get('service_type')
        request_data = data.get('data', {})
        
        result = await miniapp_service.process_miniapp_request(
            message.from_user.id,
            service_type,
            request_data
        )
        
        if result['success']:
            await message.answer(f"✅ Запрос выполнен! Стоимость: {result['cost']} звёзд")
        else:
            await message.answer(f"❌ Ошибка: {result['error']}")
            
    except Exception as e:
        logger.error(f"Ошибка обработки WebApp данных: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса")

@router.message(F.text == "💎 Пополнить баланс")
async def add_balance_handler(message: Message):
    """Обработчик пополнения баланса"""
    balance = await balance_service.get_balance(message.from_user.id)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ 100 звезд", callback_data="deposit_100"),
                InlineKeyboardButton(text="➕ 500 звезд", callback_data="deposit_500")
            ],
            [
                InlineKeyboardButton(text="➕ 1000 звезд", callback_data="deposit_1000"),
                InlineKeyboardButton(text="💳 Другая сумма", callback_data="deposit_custom")
            ],
            [
                InlineKeyboardButton(text="📊 История операций", callback_data="balance_history")
            ]
        ]
    )
    
    await message.answer(
        f"💰 <b>Ваш баланс:</b> {balance} звезд\n\n"
        "Выберите сумму для пополнения:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("deposit_"))
async def process_deposit(callback: CallbackQuery):
    """Обработчик выбора суммы пополнения"""
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "deposit_custom":
        await callback.message.answer(
            "💳 <b>Пополнение произвольной суммы</b>\n\n"
            "Введите сумму в звездах (от 10 до 5000):"
        )
        await callback.answer()
        return
    
    # Извлекаем сумму из callback_data
    amount = int(data.split("_")[1])
    
    # В реальном боте здесь была бы интеграция с платежной системой
    # Покажем демо-пополнение
    if await payment_service.add_funds(user_id, amount):
        new_balance = await balance_service.get_balance(user_id)
        await callback.message.edit_text(
            f"✅ <b>Баланс пополнен!</b>\n\n"
            f"💫 Начислено: +{amount} звезд\n"
            f"💰 Теперь у вас: {new_balance} звезд\n\n"
            f"<i>В демо-режиме средства начисляются мгновенно.</i>"
        )
    else:
        await callback.message.edit_text(
            "❌ <b>Ошибка пополнения</b>\n\n"
            "Пожалуйста, попробуйте позже."
        )
    
    await callback.answer()

@router.message(F.text == "💰 Мой баланс")
async def balance_handler(message: Message):
    """Показать баланс пользователя"""
    stats = await balance_service.get_balance_stats(message.from_user.id)
    
    balance_text = f"""
💰 <b>Ваш баланс</b>

⭐ <b>Текущий баланс:</b> {stats['balance']} звезд
📈 <b>Всего получено:</b> {stats['total_earned']} звезд
📉 <b>Всего потрачено:</b> {stats['total_spent']} звезд

💡 Звезды можно использовать для:
• Совместимость - 50 звезд
• Недельный гороскоп - 100 звезд
• Расклад Таро - 80 звезд
• Натальная карта - 200 звезд
    """
    
    await message.answer(balance_text)