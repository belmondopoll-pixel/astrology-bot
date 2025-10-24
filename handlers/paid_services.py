# paid_services.py - ДОБАВЬТЕ ЛОГИРОВАНИЕ
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, SuccessfulPayment, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import db
from keyboards import zodiac_keyboard, tarot_spreads_keyboard, main_menu
from services.gemini_service import gemini_service
from services.tarot_deck import tarot_deck
from utils.message_utils import split_message

logger = logging.getLogger(__name__)

router = Router()

# Состояния для разных процессов
class CompatibilityStates(StatesGroup):
    waiting_for_second_sign = State()

class WeeklyHoroscopeStates(StatesGroup):
    waiting_for_sign = State()

class NatalChartStates(StatesGroup):
    waiting_birth_date = State()
    waiting_birth_time = State()
    waiting_birth_place = State()

class TarotStates(StatesGroup):
    waiting_for_spread = State()

# ==================== ОБРАБОТЧИКИ С РЕАЛЬНЫМИ ПЛАТЕЖАМИ ====================

@router.message(F.text == "💑 Совместимость (55 Stars)")
async def compatibility_handler(message: Message, state: FSMContext):
    """Обработчик совместимости с реальной оплатой"""
    try:
        logger.info(f"🔄 Обработчик совместимости вызван пользователем {message.from_user.id}")
        
        user_id = message.from_user.id
        
        # Создаем инвойс для оплаты
        prices = [LabeledPrice(label="Анализ совместимости", amount=55)]
        
        logger.info(f"💰 Отправка инвойса для совместимости пользователю {user_id}")
        
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="💑 Анализ совместимости",
            description="Подробный анализ совместимости двух знаков зодиака",
            payload="compatibility_payment",
            provider_token="",  # Для Stars обычно не требуется
            currency="XTR",  # Telegram Stars
            prices=prices,
            start_parameter="compatibility"
        )
        
        await state.update_data(service_type="compatibility")
        logger.info(f"✅ Инвойс для совместимости отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в compatibility_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "📅 Гороскоп на неделю (333 Stars)")
async def weekly_horoscope_handler(message: Message, state: FSMContext):
    """Обработчик недельного гороскопа с реальной оплатой"""
    try:
        logger.info(f"🔄 Обработчик недельного гороскопа вызван пользователем {message.from_user.id}")
        
        user_id = message.from_user.id
        
        # Создаем инвойс для оплаты
        prices = [LabeledPrice(label="Гороскоп на неделю", amount=333)]
        
        logger.info(f"💰 Отправка инвойса для недельного гороскопа пользователю {user_id}")
        
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="📅 Гороскоп на неделю",
            description="Расширенный гороскоп на 7 дней с детальными прогнозами",
            payload="weekly_horoscope_payment",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="weekly_horoscope"
        )
        
        await state.update_data(service_type="weekly_horoscope")
        logger.info(f"✅ Инвойс для недельного гороскопа отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в weekly_horoscope_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "🃏 Расклад Таро (888 Stars)")
async def tarot_handler(message: Message, state: FSMContext):
    """Обработчик расклада Таро с реальной оплатой"""
    try:
        logger.info(f"🔄 Обработчик Таро вызван пользователем {message.from_user.id}")
        
        user_id = message.from_user.id
        
        # Создаем инвойс для оплаты
        prices = [LabeledPrice(label="Расклад Таро", amount=888)]
        
        logger.info(f"💰 Отправка инвойса для Таро пользователю {user_id}")
        
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="🃏 Расклад Таро",
            description="Профессиональный расклад карт Таро с интерпретацией",
            payload="tarot_payment",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="tarot"
        )
        
        await state.update_data(service_type="tarot")
        logger.info(f"✅ Инвойс для Таро отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в tarot_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "🌌 Натальная карта (999 Stars)")
async def natal_chart_handler(message: Message, state: FSMContext):
    """Обработчик натальной карты с реальной оплатой"""
    try:
        logger.info(f"🔄 Обработчик натальной карты вызван пользователем {message.from_user.id}")
        
        user_id = message.from_user.id
        
        # Создаем инвойс для оплаты
        prices = [LabeledPrice(label="Натальная карта", amount=999)]
        
        logger.info(f"💰 Отправка инвойса для натальной карты пользователю {user_id}")
        
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="🌌 Натальная карта",
            description="Персональная натальная карта по дате рождения с анализом",
            payload="natal_chart_payment",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="natal_chart"
        )
        
        await state.update_data(service_type="natal_chart")
        logger.info(f"✅ Инвойс для натальной карты отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в natal_chart_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Обработка предварительного запроса платежа"""
    logger.info(f"🔄 Pre-checkout запрос от пользователя {pre_checkout_query.from_user.id}")
    await pre_checkout_query.answer(ok=True)
    logger.info(f"✅ Pre-checkout запрос обработан")

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    """Обработка успешного платежа"""
    try:
        logger.info(f"🔄 Обработка успешного платежа от пользователя {message.from_user.id}")
        
        payment = message.successful_payment
        user_id = message.from_user.id
        
        # Определяем тип услуги по payload
        payload = payment.invoice_payload
        amount = payment.total_amount // 100  # Convert from cents
        
        logger.info(f"💰 Успешный платеж: {user_id} -> {payload} за {amount} Stars")
        
        # Логируем платеж в базу
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payments (user_id, service_type, amount_stars, status, payment_data)
                VALUES (?, ?, ?, 'completed', ?)
            ''', (user_id, payload, amount, str(payment)))
            conn.commit()
        
        logger.info(f"📊 Платеж записан в базу данных")
        
        # Предоставляем услугу в зависимости от типа
        if payload == "compatibility_payment":
            await message.answer(
                "💑 <b>Оплата принята!</b>\n\n"
                "Теперь выберите первый знак зодиака для анализа совместимости:",
                reply_markup=zodiac_keyboard("compatibility_first_paid")
            )
            logger.info(f"✅ Начало процесса совместимости для пользователя {user_id}")
            
        elif payload == "weekly_horoscope_payment":
            await message.answer(
                "📅 <b>Оплата принята!</b>\n\n"
                "Теперь выберите ваш знак зодиака для гороскопа на неделю:",
                reply_markup=zodiac_keyboard("weekly_horoscope_paid")
            )
            logger.info(f"✅ Начало процесса недельного гороскопа для пользователя {user_id}")
            
        elif payload == "tarot_payment":
            await message.answer(
                "🃏 <b>Оплата принята!</b>\n\n"
                "Теперь выберите тип расклада Таро:",
                reply_markup=tarot_spreads_keyboard()
            )
            logger.info(f"✅ Начало процесса Таро для пользователя {user_id}")
            
        elif payload == "natal_chart_payment":
            await message.answer(
                "🌌 <b>Оплата принята!</b>\n\n"
                "Для составления натальной карты мне понадобятся:\n"
                "1. Дата рождения (ДД.ММ.ГГГГ)\n"
                "2. Время рождения (ЧЧ:ММ)\n" 
                "3. Место рождения (Город, Страна)\n\n"
                "Введите дату рождения в формате ДД.ММ.ГГГГ:"
            )
            await state.set_state(NatalChartStates.waiting_birth_date)
            logger.info(f"✅ Начало процесса натальной карты для пользователя {user_id}")
            
        await state.update_data(paid_service=payload)
        logger.info(f"🎉 Услуга активирована для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в successful_payment_handler: {e}")
        await message.answer("❌ Произошла ошибка при обработке платежа.")

# Обработчики для оплаченных услуг
@router.callback_query(F.data.startswith("compatibility_first_paid_"))
async def process_first_sign_paid(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора первого знака для оплаченной совместимости"""
    try:
        await callback.answer()
        
        first_sign = callback.data.split("_")[3]
        await state.update_data(first_sign=first_sign)
        
        logger.info(f"🔄 Пользователь {callback.from_user.id} выбрал первый знак: {first_sign}")
        
        await callback.message.edit_text(
            f"✅ Первый знак: <b>{first_sign}</b>\n\n"
            "Теперь выберите второй знак зодиака:",
            reply_markup=zodiac_keyboard("compatibility_second_paid")
        )
    except Exception as e:
        logger.error(f"❌ Ошибка в process_first_sign_paid: {e}")
        await callback.answer("❌ Ошибка выбора знака")

@router.callback_query(F.data.startswith("compatibility_second_paid_"))
async def process_second_sign_paid(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора второго знака для оплаченной совместимости"""
    try:
        await callback.answer()
        
        second_sign = callback.data.split("_")[3]
        user_data = await state.get_data()
        first_sign = user_data.get('first_sign')
        user_id = callback.from_user.id
        
        logger.info(f"🔄 Пользователь {user_id} выбрал второй знак: {second_sign}")
        
        if not first_sign:
            await callback.message.edit_text("❌ Не выбран первый знак. Начните заново.")
            await state.clear()
            return

        await callback.message.edit_text(
            f"💑 <b>Генерирую анализ совместимости для {first_sign} и {second_sign}...</b>\n\n"
            f"<em>Это может занять несколько секунд</em>"
        )
        
        # Предоставляем оплаченную услугу
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
        logger.error(f"❌ Ошибка в process_second_sign_paid: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при обработке запроса.")

@router.callback_query(F.data.startswith("weekly_horoscope_paid_"))
async def process_weekly_horoscope_paid(callback: CallbackQuery, state: FSMContext):
    """Обработчик генерации оплаченного недельного гороскопа"""
    try:
        await callback.answer()
        
        zodiac_sign = callback.data.split("_")[3]
        user_id = callback.from_user.id
        
        logger.info(f"🔄 Генерация недельного гороскопа для {zodiac_sign} пользователем {user_id}")
        
        await callback.message.edit_text(
            f"📅 <b>Генерирую гороскоп на неделю для {zodiac_sign}...</b>\n\n"
            f"<em>Это может занять несколько секунд</em>"
        )
        
        # Предоставляем оплаченную услугу
        horoscope_text = await gemini_service.generate_weekly_horoscope(zodiac_sign)
        
        await callback.message.edit_text(
            f"📅 <b>Гороскоп на неделю для {zodiac_sign}</b>\n\n"
            f"{horoscope_text}\n\n"
            f"<i>✅ Услуга оплачена • 333 Stars</i>"
        )
        
        # Логируем запрос
        db.log_request(user_id, f"weekly_horoscope_{zodiac_sign}", 333)
        logger.info(f"✅ Услуга недельного гороскопа предоставлена пользователю {user_id}")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_weekly_horoscope_paid: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")

@router.callback_query(F.data.startswith("tarot_"))
async def process_tarot_spread_paid(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора расклада Таро для оплаченной услуги"""
    try:
        await callback.answer()
        
        spread_type = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        logger.info(f"🔄 Генерация расклада Таро {spread_type} для пользователя {user_id}")
        
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
        
        # Предоставляем оплаченную услугу
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
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в process_tarot_spread_paid: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")

# Обработчики для натальной карты (уже оплаченной)
@router.message(NatalChartStates.waiting_birth_date)
async def process_birth_date_paid(message: Message, state: FSMContext):
    """Обработка даты рождения для оплаченной натальной карты"""
    birth_date = message.text.strip()
    
    logger.info(f"🔄 Обработка даты рождения от пользователя {message.from_user.id}: {birth_date}")
    
    if not await validate_date_format(birth_date):
        await message.answer("❌ Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например, 15.05.1990):")
        return

    await state.update_data(birth_date=birth_date)
    await state.set_state(NatalChartStates.waiting_birth_time)
    await message.answer("✅ Дата сохранена. Теперь введите время рождения в формате ЧЧ:ММ (например, 14:30):")

@router.message(NatalChartStates.waiting_birth_time)
async def process_birth_time_paid(message: Message, state: FSMContext):
    """Обработка времени рождения для оплаченной натальной карты"""
    birth_time = message.text.strip()
    
    logger.info(f"🔄 Обработка времени рождения от пользователя {message.from_user.id}: {birth_time}")
    
    if not await validate_time_format(birth_time):
        await message.answer("❌ Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 14:30):")
        return

    await state.update_data(birth_time=birth_time)
    await state.set_state(NatalChartStates.waiting_birth_place)
    await message.answer("✅ Время сохранено. Теперь введите место рождения (город, страна):")

@router.message(NatalChartStates.waiting_birth_place)
async def process_birth_place_paid(message: Message, state: FSMContext):
    """Обработка места рождения и создание натальной карты для оплаченной услуги"""
    birth_place = message.text.strip()
    user_id = message.from_user.id
    user_data = await state.get_data()
    
    logger.info(f"🔄 Обработка места рождения от пользователя {user_id}: {birth_place}")
    
    if not birth_place:
        await message.answer("❌ Место рождения не может быть пустым. Пожалуйста, введите место рождения:")
        return

    await state.update_data(birth_place=birth_place)
    
    birth_date = user_data.get('birth_date')
    birth_time = user_data.get('birth_time')

    generating_msg = await message.answer(
        f"🌌 <b>Генерирую натальную карту...</b>\n\n"
        f"<em>Дата: {birth_date}\n"
        f"Время: {birth_time}\n"
        f"Место: {birth_place}</em>\n\n"
        "Это может занять несколько секунд."
    )
    
    # Предоставляем оплаченную услугу
    birth_data = {
        'birth_date': birth_date,
        'birth_time': birth_time, 
        'birth_place': birth_place
    }
    
    natal_chart_text = await gemini_service.generate_natal_chart_interpretation(birth_data)
    
    await generating_msg.edit_text(
        f"🌌 <b>Ваша натальная карта</b>\n\n"
        f"<b>Данные:</b>\n"
        f"📅 Дата: {birth_date}\n"
        f"⏰ Время: {birth_time}\n"
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