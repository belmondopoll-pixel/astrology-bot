# handlers/paid_services.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import db
from keyboards import zodiac_keyboard, tarot_spreads_keyboard
from services.stars_payment_service import stars_payment_service
from services.gemini_service import gemini_service
from services.tarot_deck import tarot_deck

logger = logging.getLogger(__name__)

router = Router()

class NatalChartStates(StatesGroup):
    waiting_birth_date = State()
    waiting_birth_time = State()
    waiting_birth_place = State()

# ==================== ОБРАБОТЧИКИ ПЛАТНЫХ УСЛУГ С РЕАЛЬНОЙ ОПЛАТОЙ ====================

@router.message(F.text == "💑 Совместимость (55 Stars)")
async def compatibility_handler(message: Message):
    """Обработчик совместимости с реальной оплатой"""
    try:
        logger.info(f"🎯 Обработчик совместимости ВЫЗВАН для пользователя {message.from_user.id}")
        
        await message.answer(
            "💑 <b>Анализ совместимости</b>\n\n"
            "Выберите первый знак зодиака:",
            reply_markup=zodiac_keyboard("compat_first")
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в compatibility_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("compat_first_"))
async def process_first_sign(callback: CallbackQuery, state: FSMContext):
    """Обработчик первого знака"""
    try:
        await callback.answer()
        sign = callback.data.split("_")[2]
        logger.info(f"🎯 Обработчик первого знака: {sign}")
        
        await state.update_data(first_sign=sign)
        
        await callback.message.edit_text(
            f"✅ Первый знак: <b>{sign}</b>\n\n"
            "Выберите второй знак зодиака:",
            reply_markup=zodiac_keyboard("compat_second")
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_first_sign: {e}")

@router.callback_query(F.data.startswith("compat_second_"))
async def process_second_sign(callback: CallbackQuery, state: FSMContext):
    """Обработчик второго знака с отправкой инвойса"""
    try:
        await callback.answer()
        second_sign = callback.data.split("_")[2]
        user_data = await state.get_data()
        first_sign = user_data.get('first_sign')
        user_id = callback.from_user.id
        
        logger.info(f"🎯 Обработчик второго знака: {second_sign}, первый: {first_sign}")
        
        if not first_sign:
            await callback.message.edit_text("❌ Не выбран первый знак. Начните заново.")
            return

        # Создаем инвойс для оплаты
        invoice = stars_payment_service.get_invoice("compatibility", {
            'first_sign': first_sign,
            'second_sign': second_sign
        })
        
        # Отправляем инвойс для оплаты через Telegram Stars
        await callback.message.answer_invoice(
            title=invoice["title"],
            description=invoice["description"],
            payload=invoice["payload"],
            currency=invoice["currency"],  # "XTR" для Telegram Stars
            prices=invoice["prices"],
            start_parameter=invoice["start_parameter"],
            # provider_token НЕ требуется для Telegram Stars
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_second_sign: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при обработке запроса.")

@router.message(F.text == "📅 Гороскоп на неделю (333 Stars)")
async def weekly_horoscope_handler(message: Message):
    """Обработчик недельного гороскопа с реальной оплатой"""
    try:
        logger.info(f"🎯 Обработчик недельного гороскопа ВЫЗВАН для пользователя {message.from_user.id}")
        
        await message.answer(
            "📅 <b>Гороскоп на неделю</b>\n\n"
            "Выберите ваш знак зодиака:",
            reply_markup=zodiac_keyboard("weekly_paid")
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в weekly_horoscope_handler: {e}")

@router.callback_query(F.data.startswith("weekly_paid_"))
async def process_weekly_horoscope(callback: CallbackQuery):
    """Обработчик недельного гороскопа с отправкой инвойса"""
    try:
        await callback.answer()
        zodiac_sign = callback.data.split("_")[2]
        user_id = callback.from_user.id
        
        logger.info(f"🎯 Обработчик недельного гороскопа для: {zodiac_sign}")
        
        # Создаем инвойс для оплаты
        invoice = stars_payment_service.get_invoice("weekly_horoscope", {
            'zodiac_sign': zodiac_sign
        })
        
        # Отправляем инвойс для оплаты через Telegram Stars
        await callback.message.answer_invoice(
            title=invoice["title"],
            description=invoice["description"],
            payload=invoice["payload"],
            currency=invoice["currency"],
            prices=invoice["prices"],
            start_parameter=invoice["start_parameter"]
            # provider_token НЕ требуется для Telegram Stars
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_weekly_horoscope: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")

@router.message(F.text == "🃏 Расклад Таро (888 Stars)")
async def tarot_handler(message: Message):
    """Обработчик расклада Таро с реальной оплатой"""
    try:
        logger.info(f"🎯 Обработчик Таро ВЫЗВАН для пользователя {message.from_user.id}")
        
        await message.answer(
            "🃏 <b>Расклад карт Таро</b>\n\n"
            "Выберите тип расклада:",
            reply_markup=tarot_spreads_keyboard()
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в tarot_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("tarot_"))
async def process_tarot_spread(callback: CallbackQuery):
    """Обработчик расклада Таро с отправкой инвойса"""
    try:
        await callback.answer()
        spread_type = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        logger.info(f"🎯 Обработчик Таро для расклада: {spread_type}")
        
        # Создаем инвойс для оплаты
        invoice = stars_payment_service.get_invoice("tarot", {
            'spread_type': spread_type
        })
        
        # Отправляем инвойс для оплаты через Telegram Stars
        await callback.message.answer_invoice(
            title=invoice["title"],
            description=invoice["description"],
            payload=invoice["payload"],
            currency=invoice["currency"],
            prices=invoice["prices"],
            start_parameter=invoice["start_parameter"]
            # provider_token НЕ требуется для Telegram Stars
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_tarot_spread: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")

@router.message(F.text == "🌌 Натальная карта (999 Stars)")
async def natal_chart_handler(message: Message, state: FSMContext):
    """Обработчик натальной карты с реальной оплатой"""
    try:
        logger.info(f"🎯 Обработчик натальной карты ВЫЗВАН для пользователя {message.from_user.id}")
        
        await message.answer(
            "🌌 <b>Натальная карта</b>\n\n"
            "Для составления натальной карты мне понадобятся:\n"
            "1. Дата рождения (ДД.ММ.ГГГГ)\n"
            "2. Время рождения (ЧЧ:ММ)\n" 
            "3. Место рождения (Город, Страна)\n\n"
            "Введите дату рождения в формате ДД.ММ.ГГГГ:"
        )
        
        await state.set_state(NatalChartStates.waiting_birth_date)
        
    except Exception as e:
        logger.error(f"❌ Ошибка в natal_chart_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(NatalChartStates.waiting_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    """Обработка даты рождения"""
    birth_date = message.text.strip()
    
    logger.info(f"🎯 Обработка даты рождения: {birth_date}")
    
    if not await validate_date_format(birth_date):
        await message.answer("❌ Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например, 15.05.1990):")
        return

    await state.update_data(birth_date=birth_date)
    await state.set_state(NatalChartStates.waiting_birth_time)
    await message.answer("✅ Дата сохранена. Теперь введите время рождения в формате ЧЧ:ММ (например, 14:30):")

@router.message(NatalChartStates.waiting_birth_time)
async def process_birth_time(message: Message, state: FSMContext):
    """Обработка времени рождения"""
    birth_time = message.text.strip()
    
    logger.info(f"🎯 Обработка времени рождения: {birth_time}")
    
    if not await validate_time_format(birth_time):
        await message.answer("❌ Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 14:30):")
        return

    await state.update_data(birth_time=birth_time)
    await state.set_state(NatalChartStates.waiting_birth_place)
    await message.answer("✅ Время сохранено. Теперь введите место рождения (город, страна):")

@router.message(NatalChartStates.waiting_birth_place)
async def process_birth_place(message: Message, state: FSMContext):
    """Обработка места рождения и отправка инвойса"""
    birth_place = message.text.strip()
    user_id = message.from_user.id
    user_data = await state.get_data()
    
    logger.info(f"🎯 Обработка места рождения: {birth_place}")
    
    if not birth_place:
        await message.answer("❌ Место рождения не может быть пустым. Пожалуйста, введите место рождения:")
        return

    # Сохраняем данные в состоянии для использования после оплаты
    birth_data = {
        'birth_date': user_data.get('birth_date'),
        'birth_time': user_data.get('birth_time'), 
        'birth_place': birth_place
    }
    
    await state.update_data(birth_data=birth_data)
    
    # Создаем инвойс для оплаты
    invoice = stars_payment_service.get_invoice("natal", {
        'birth_data': birth_data
    })
    
    # Отправляем инвойс для оплаты через Telegram Stars
    await message.answer_invoice(
        title=invoice["title"],
        description=invoice["description"],
        payload=invoice["payload"],
        currency=invoice["currency"],
        prices=invoice["prices"],
        start_parameter=invoice["start_parameter"]
        # provider_token НЕ требуется для Telegram Stars
    )

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

async def validate_date_format(date_str: str) -> bool:
    """Проверка формата даты"""
    try:
        parts = date_str.split('.')
        if len(parts) != 3:
            return False
        day, month, year = parts
        if len(day) != 2 or len(month) != 2 or len(year) != 4:
            return False
        int(day), int(month), int(year)
        return True
    except:
        return False

async def validate_time_format(time_str: str) -> bool:
    """Проверка формата времени"""
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            return False
        hour, minute = parts
        if len(hour) != 2 or len(minute) != 2:
            return False
        h, m = int(hour), int(minute)
        if h < 0 or h > 23 or m < 0 or m > 59:
            return False
        return True
    except:
        return False