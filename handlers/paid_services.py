# handlers/paid_services.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import db
from keyboards import zodiac_keyboard, tarot_spreads_keyboard
from services.gemini_service import gemini_service
from services.tarot_deck import tarot_deck

logger = logging.getLogger(__name__)

router = Router()

class NatalChartStates(StatesGroup):
    waiting_birth_date = State()
    waiting_birth_time = State()
    waiting_birth_place = State()

# ==================== ДИАГНОСТИКА ====================

@router.message()
async def debug_paid_messages(message: Message):
    """Диагностический обработчик для платных услуг"""
    if message.text in ["💑 Совместимость (55 Stars)", "📅 Гороскоп на неделю (333 Stars)", 
                       "🃏 Расклад Таро (888 Stars)", "🌌 Натальная карта (999 Stars)"]:
        logger.info(f"🔍 Платная услуга получена но не обработана: {message.text} от пользователя {message.from_user.id}")

# ==================== ОБРАБОТЧИКИ ПЛАТНЫХ УСЛУГ ====================

@router.message(F.text == "💑 Совместимость (55 Stars)")
async def compatibility_handler(message: Message):
    """Обработчик совместимости"""
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
    """Обработчик второго знака"""
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

        await callback.message.edit_text(
            f"💑 <b>Генерирую анализ совместимости для {first_sign} и {second_sign}...</b>\n\n"
            f"<em>Это может занять несколько секунд</em>"
        )
        
        # Предоставляем услугу
        compatibility_text = await gemini_service.generate_compatibility(first_sign, second_sign)
        
        await callback.message.edit_text(
            f"💑 <b>Совместимость: {first_sign} и {second_sign}</b>\n\n"
            f"{compatibility_text}\n\n"
            f"<i>✅ Услуга оплачена • 55 Stars</i>"
        )
        
        # Логируем запрос
        db.log_request(user_id, f"compatibility_{first_sign}_{second_sign}", 55)
        logger.info(f"✅ Услуга совместимости предоставлена пользователю {user_id}")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_second_sign: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при обработке запроса.")

@router.message(F.text == "📅 Гороскоп на неделю (333 Stars)")
async def weekly_horoscope_handler(message: Message):
    """Обработчик недельного гороскопа"""
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
    """Обработчик недельного гороскопа"""
    try:
        await callback.answer()
        zodiac_sign = callback.data.split("_")[2]
        user_id = callback.from_user.id
        
        logger.info(f"🎯 Обработчик недельного гороскопа для: {zodiac_sign}")
        
        await callback.message.edit_text(
            f"📅 <b>Генерирую гороскоп на неделю для {zodiac_sign}...</b>\n\n"
            f"<em>Это может занять несколько секунд</em>"
        )
        
        # Предоставляем услугу
        horoscope_text = await gemini_service.generate_weekly_horoscope(zodiac_sign)
        
        await callback.message.edit_text(
            f"📅 <b>Гороскоп на неделю для {zodiac_sign}</b>\n\n"
            f"{horoscope_text}\n\n"
            f"<i>✅ Услуга оплачена • 333 Stars</i>"
        )
        
        # Логируем запрос
        db.log_request(user_id, f"weekly_horoscope_{zodiac_sign}", 333)
        logger.info(f"✅ Услуга недельного гороскопа предоставлена пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_weekly_horoscope: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")

@router.message(F.text == "🃏 Расклад Таро (888 Stars)")
async def tarot_handler(message: Message):
    """Обработчик расклада Таро"""
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
    """Обработчик расклада Таро"""
    try:
        await callback.answer()
        spread_type = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        logger.info(f"🎯 Обработчик Таро для расклада: {spread_type}")
        
        spread_names = {
            "celtic": "Кельтский крест",
            "three": "Прошлое-Настоящее-Будущее", 
            "four": "Ситуация-Вызовы-Совет-Результат",
            "daily": "Карта дня"
        }
        
        spread_name = spread_names.get(spread_type, "Выбранный расклад")
        
        await callback.message.edit_text(
            f"🃏 <b>Готовлю расклад '{spread_name}'...</b>\n\n"
            f"<em>Перемешиваю карты...</em>"
        )
        
        # Предоставляем услугу
        cards, positions = tarot_deck.create_spread(spread_type)
        
        spread_description = ""
        for i, card in enumerate(cards):
            position_name = positions[i] if i < len(positions) else f"Позиция {i+1}"
            orientation = "прямое" if card["position"] == "upright" else "перевернутое"
            spread_description += f"{position_name}: {card['name']} ({orientation})\n"
        
        interpretation = await gemini_service.generate_tarot_reading(spread_type, spread_description)
        
        # Форматируем результат
        cards_text = "🎴 Ваш расклад:\n\n"
        for i, card in enumerate(cards):
            position_name = positions[i] if i < len(positions) else f"Позиция {i+1}"
            orientation = "🔼" if card["position"] == "upright" else "🔽"
            cards_text += f"{orientation} <b>{position_name}:</b>\n"
            cards_text += f"   🃏 {card['name']}\n"
            cards_text += f"   📖 {tarot_deck.get_card_meaning(card)}\n\n"
        
        full_content = f"{cards_text}\n💫 <b>Интерпретация:</b>\n\n{interpretation}"
        
        await callback.message.edit_text(
            f"🃏 <b>{spread_name}</b>\n\n"
            f"{full_content}\n\n"
            f"<i>✅ Услуга оплачена • 888 Stars</i>"
        )
        
        # Логируем запрос
        db.log_request(user_id, f"tarot_{spread_type}", 888)
        logger.info(f"✅ Услуга Таро предоставлена пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_tarot_spread: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")

@router.message(F.text == "🌌 Натальная карта (999 Stars)")
async def natal_chart_handler(message: Message, state: FSMContext):
    """Обработчик натальной карты"""
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
    """Обработка места рождения"""
    birth_place = message.text.strip()
    user_id = message.from_user.id
    user_data = await state.get_data()
    
    logger.info(f"🎯 Обработка места рождения: {birth_place}")
    
    if not birth_place:
        await message.answer("❌ Место рождения не может быть пустым. Пожалуйста, введите место рождения:")
        return

    generating_msg = await message.answer(
        f"🌌 <b>Генерирую натальную карту...</b>\n\n"
        f"<em>Дата: {user_data.get('birth_date')}\n"
        f"Время: {user_data.get('birth_time')}\n"
        f"Место: {birth_place}</em>\n\n"
        "Это может занять несколько секунд."
    )
    
    # Предоставляем услугу
    birth_data = {
        'birth_date': user_data.get('birth_date'),
        'birth_time': user_data.get('birth_time'), 
        'birth_place': birth_place
    }
    
    natal_chart_text = await gemini_service.generate_natal_chart_interpretation(birth_data)
    
    await generating_msg.edit_text(
        f"🌌 <b>Ваша натальная карта</b>\n\n"
        f"<b>Данные:</b>\n"
        f"📅 Дата: {user_data.get('birth_date')}\n"
        f"⏰ Время: {user_data.get('birth_time')}\n"
        f"📍 Место: {birth_place}\n\n"
        f"{natal_chart_text}\n\n"
        f"<i>✅ Услуга оплачена • 999 Stars</i>"
    )
    
    # Логируем запрос
    db.log_request(user_id, "natal_chart", 999)
    logger.info(f"✅ Услуга натальной карты предоставлена пользователю {user_id}")
    
    await state.clear()

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