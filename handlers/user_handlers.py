# user_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import db
from keyboards import main_menu, zodiac_keyboard, web_app_keyboard, get_webapp_url
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

router = Router()

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
    
    user_balance = db.get_user_balance(message.from_user.id)
    
    welcome_text = f"""
🌟 <b>Добро пожаловать в АстроБот!</b> 🌟

Ваш баланс: <b>{user_balance} Stars</b>

Я ваш личный астрологический помощник. Вот что я умею:

<b>Бесплатные услуги:</b>
♈ Ежедневный гороскоп
📚 Общая информация об астрологии

<b>Платные услуги (Telegram Stars):</b>
💑 Совместимость по знакам зодиака - 55 Stars
📅 Расширенный гороскоп на неделю - 333 Stars  
🌌 Натальная карта с интерпретацией - 999 Stars
🃏 Расклад карт Таро - 888 Stars

💫 <i>Все платежи обрабатываются через Telegram Stars. Нажмите на услугу для оплаты.</i>

📱 <b>Также доступно удобное MiniApp с красивым интерфейсом!</b>
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
    
    await callback.answer()
    
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

@router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Показать баланс пользователя"""
    user_balance = db.get_user_balance(message.from_user.id)
    await message.answer(
        f"💰 <b>Ваш баланс</b>\n\n"
        f"Доступно: <b>{user_balance} Telegram Stars</b>\n\n"
        f"Для пополнения баланса используйте команду /buy_tokens"
    )

@router.message(Command("buy_tokens"))
async def cmd_buy_tokens(message: Message):
    """Покупка токенов"""
    await message.answer(
        "💰 <b>Пополнение баланса</b>\n\n"
        "Для пополнения баланса Telegram Stars:\n\n"
        "1. Откройте чат с @BotFather\n"
        "2. Выберите вашего бота\n"
        "3. Нажмите \"Payments\"\n"
        "4. Следуйте инструкциям для настройки платежей\n\n"
        "После настройки пользователи смогут отправлять вам Stars напрямую через бота!"
    )

@router.message()
async def debug_handler(message: Message):
    """Обработчик для диагностики необработанных сообщений"""
    logger.info(f"🔍 Необработанное сообщение: {message.text} от пользователя {message.from_user.id}")
    await message.answer("Извините, я не понял ваше сообщение. Используйте меню для навигации.")