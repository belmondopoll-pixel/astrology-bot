from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import db
from keyboards import zodiac_keyboard, tarot_spreads_keyboard
from services.gemini_service import gemini_service
from services.payment_service import payment_service
from services.tarot_deck import tarot_deck
from utils.message_utils import split_message

logger = logging.getLogger(__name__)

# СОЗДАЕМ РОУТЕР ДЛЯ ПЛАТНЫХ УСЛУГ
router = Router()

# Состояния для разных процессов
class CompatibilityStates(StatesGroup):
    waiting_for_second_sign = State()

class WeeklyHoroscopeStates(StatesGroup):
    waiting_for_user_data = State()

class NatalChartStates(StatesGroup):
    waiting_birth_date = State()
    waiting_birth_time = State()
    waiting_birth_place = State()

class TarotStates(StatesGroup):
    waiting_for_spread = State()
    waiting_for_question = State()

# ==================== ОБРАБОТЧИКИ ПЛАТНЫХ УСЛУГ ====================

@router.message(F.text == "💑 Совместимость (50 звёзд)")
async def compatibility_handler(message: Message, state: FSMContext):
    """Обработчик совместимости"""
    try:
        invoice = await payment_service.create_invoice(
            message.from_user.id,
            "compatibility",
            "Анализ совместимости по знакам зодиака"
        )
        
        await message.answer(
            f"💑 <b>Совместимость по знакам зодиака</b>\n\n"
            f"{invoice['instructions']}\n\n"
            f"Для продолжения выберите первый знак зодиака:",
            reply_markup=zodiac_keyboard("compatibility_first")
        )
    except Exception as e:
        logger.error(f"Ошибка в compatibility_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("compatibility_first_"))
async def process_first_sign(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора первого знака для совместимости"""
    try:
        first_sign = callback.data.split("_")[2]
        
        await state.update_data(first_sign=first_sign)
        await state.set_state(CompatibilityStates.waiting_for_second_sign)
        
        await callback.message.edit_text(
            f"Выбран первый знак: <b>{first_sign}</b>\n\n"
            "Теперь выберите второй знак зодиака:",
            reply_markup=zodiac_keyboard("compatibility_second")
        )
    except Exception as e:
        logger.error(f"Ошибка в process_first_sign: {e}")
        await callback.answer("❌ Ошибка выбора знака")

@router.callback_query(F.data.startswith("compatibility_second_"))
async def process_second_sign(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора второго знака и генерация совместимости"""
    try:
        second_sign = callback.data.split("_")[2]
        user_data = await state.get_data()
        first_sign = user_data.get('first_sign')
        
        if not first_sign:
            await callback.message.edit_text("❌ Не выбран первый знак. Начните заново.")
            await state.clear()
            return

        # Проверяем оплату
        if await payment_service.process_payment(callback.from_user.id, "compatibility"):
            # Логируем запрос
            db.log_request(callback.from_user.id, "compatibility")
            
            await callback.message.edit_text(
                f"💑 Генерирую анализ совместимости для <b>{first_sign}</b> и <b>{second_sign}</b>...\n\n"
                "<em>Это может занять несколько секунд</em>"
            )
            
            try:
                compatibility_text = await gemini_service.generate_compatibility(first_sign, second_sign)
                
                # Разбиваем длинное сообщение на части
                header = f"💑 <b>Совместимость: {first_sign} и {second_sign}</b>\n\n"
                footer = "\n\n<i>Услуга оплачена (50 звёзд)</i>"
                
                # Первая часть с заголовком
                first_part = header + compatibility_text[:4000 - len(header + footer)] + footer
                await callback.message.edit_text(first_part)
                
                # Если текст длинный, отправляем остальные части
                if len(compatibility_text) > 4000:
                    remaining_text = compatibility_text[4000 - len(header + footer):]
                    message_parts = split_message(remaining_text, 4000)
                    
                    for part in message_parts:
                        await callback.message.answer(part)
                
            except Exception as e:
                error_text = (
                    f"❌ Произошла ошибка при генерации совместимости.\n\n"
                    f"<em>Ошибка: {str(e)}</em>\n\n"
                    f"Средства не были списаны."
                )
                await callback.message.edit_text(error_text)
        else:
            await callback.message.edit_text(
                "❌ <b>Недостаточно средств</b>\n\n"
                "Для использования этой услуги требуется 50 Telegram Stars.\n"
                "Пополните баланс и попробуйте снова."
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в process_second_sign: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при обработке запроса.")
    
    await callback.answer()

@router.message(F.text == "📅 Гороскоп на неделю (100 звёзд)")
async def weekly_horoscope_handler(message: Message):
    """Обработчик недельного гороскопа"""
    try:
        await message.answer(
            "📅 <b>Расширенный гороскоп на неделю</b>\n\n"
            "Выберите знак зодиака для получения подробного гороскопа на неделю:",
            reply_markup=zodiac_keyboard("weekly_horoscope")
        )
    except Exception as e:
        logger.error(f"Ошибка в weekly_horoscope_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("weekly_horoscope_"))
async def process_weekly_horoscope(callback: CallbackQuery):
    """Обработчик генерации недельного гороскопа"""
    try:
        zodiac_sign = callback.data.split("_")[2]
        
        # Проверяем оплату
        if await payment_service.process_payment(callback.from_user.id, "weekly_horoscope"):
            db.log_request(callback.from_user.id, "weekly_horoscope")
            
            await callback.message.edit_text(
                f"📅 Генерирую расширенный гороскоп на неделю для <b>{zodiac_sign}</b>..."
            )
            
            try:
                weekly_horoscope = await gemini_service.generate_weekly_horoscope(zodiac_sign)
                
                # Разбиваем длинное сообщение на части
                header = f"📅 <b>Расширенный гороскоп на неделю для {zodiac_sign}</b>\n\n"
                footer = "\n\n<i>Услуга оплачена (100 звёзд)</i>"
                
                # Первая часть с заголовком
                first_part = header + weekly_horoscope[:4000 - len(header + footer)] + footer
                await callback.message.edit_text(first_part)
                
                # Если текст длинный, отправляем остальные части
                if len(weekly_horoscope) > 4000:
                    remaining_text = weekly_horoscope[4000 - len(header + footer):]
                    message_parts = split_message(remaining_text, 4000)
                    
                    for part in message_parts:
                        await callback.message.answer(part)
                
            except Exception as e:
                await callback.message.edit_text(f"❌ Ошибка генерации: {str(e)}")
        else:
            await callback.message.edit_text("❌ Недостаточно средств")
            
    except Exception as e:
        logger.error(f"Ошибка в process_weekly_horoscope: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")
    
    await callback.answer()

@router.message(F.text == "🃏 Расклад Таро (80 звёзд)")
async def tarot_handler(message: Message):
    """Обработчик расклада Таро"""
    try:
        await message.answer(
            "🃏 <b>Расклад карт Таро</b>\n\n"
            "Я перемешаю колоду и вытяну карты для вашего расклада.\n\n"
            "Выберите тип расклада:",
            reply_markup=tarot_spreads_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в tarot_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("tarot_"))
async def process_tarot_spread(callback: CallbackQuery):
    """Обработчик выбора расклада Таро"""
    try:
        spread_type = callback.data.split("_")[1]
        
        spread_names = {
            "celtic": "Кельтский крест",
            "three": "Расклад на 3 карты", 
            "four": "Расклад на 4 карты",
            "daily": "Карта дня"
        }
        
        spread_name = spread_names.get(spread_type, "Выбранный расклад")
        
        # Проверяем оплату
        if await payment_service.process_payment(callback.from_user.id, "tarot_reading"):
            db.log_request(callback.from_user.id, f"tarot_{spread_type}")
            
            # Показываем анимацию тасования
            await callback.message.edit_text(
                f"🃏 Готовлю колоду для расклада '{spread_name}'...\n\n"
                "<em>Перемешиваю карты...</em>"
            )
            
            try:
                # Создаем расклад
                cards, positions = tarot_deck.create_spread(spread_type)
                
                # Отображаем карты пользователю
                cards_display = tarot_deck.format_spread_for_display(cards)
                await callback.message.edit_text(cards_display)
                
                # Генерируем интерпретацию через Gemini
                await callback.message.answer(
                    "🧠 <b>Генерирую интерпретацию расклада...</b>\n\n"
                    "<em>Это может занять несколько секунд</em>"
                )
                
                # Создаем промпт для Gemini
                spread_description = create_tarot_prompt(spread_type, cards, positions)
                tarot_reading = await gemini_service.generate_tarot_reading(spread_type, spread_description)
                
                # Отправляем интерпретацию
                interpretation_header = f"🔮 <b>Интерпретация расклада '{spread_name}'</b>\n\n"
                full_interpretation = interpretation_header + tarot_reading + "\n\n<i>Услуга оплачена (80 звёзд)</i>"
                
                # Разбиваем длинное сообщение если нужно
                message_parts = split_message(full_interpretation, 4000)
                for part in message_parts:
                    await callback.message.answer(part)
                
            except Exception as e:
                await callback.message.edit_text(f"❌ Ошибка генерации расклада: {str(e)}")
        else:
            await callback.message.edit_text("❌ Недостаточно средств")
            
    except Exception as e:
        logger.error(f"Ошибка в process_tarot_spread: {e}")
        await callback.message.edit_text("❌ Произошла ошибка")
    
    await callback.answer()

def create_tarot_prompt(spread_type, cards, positions):
    """Создание промпта для Gemini на основе выпавших карт"""
    
    spread_descriptions = {
        "celtic": "Кельтский крест - глубокий анализ текущей ситуации и ее развития",
        "three": "Расклад на три карты: Прошлое, Настоящее, Будущее",
        "four": "Расклад на четыре карты: Ситуация, Вызовы, Совет, Результат", 
        "daily": "Карта дня - совет на сегодняшний день"
    }
    
    prompt = f"""
    Проинтерпретируй расклад Таро: {spread_descriptions.get(spread_type, spread_type)}
    
    Выпавшие карты и их позиции:
    """
    
    for i, card in enumerate(cards):
        position = positions[i] if i < len(positions) else f"Позиция {i+1}"
        orientation = "прямое" if card["position"] == "upright" else "перевернутое"
        prompt += f"\n- {position}: {card['name']} ({orientation} положение)"
        if "upright" in card:
            prompt += f" - {card['upright'] if card['position'] == 'upright' else card['reversed']}"
    
    prompt += """
    
    Проанализируй:
    1. Общую энергетику расклада
    2. Значение каждой карты в ее позиции
    3. Взаимосвязи между картами
    4. Практические рекомендации
    5. Потенциальные развития ситуации
    
    Будь мудрым и поддерживающим. Избегай категоричных предсказаний.
    Объем: 300-400 слов. На русском языке.
    """
    
    return prompt

@router.message(F.text == "🌌 Натальная карта (200 звёзд)")
async def natal_chart_handler(message: Message, state: FSMContext):
    """Обработчик натальной карты"""
    try:
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
        logger.error(f"Ошибка в natal_chart_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(NatalChartStates.waiting_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    """Обработка даты рождения"""
    birth_date = message.text.strip()
    # Простая валидация формата даты
    if not validate_date_format(birth_date):
        await message.answer("❌ Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например, 15.05.1990):")
        return

    await state.update_data(birth_date=birth_date)
    await state.set_state(NatalChartStates.waiting_birth_time)
    await message.answer("✅ Дата сохранена. Теперь введите время рождения в формате ЧЧ:ММ (например, 14:30):")

@router.message(NatalChartStates.waiting_birth_time)
async def process_birth_time(message: Message, state: FSMContext):
    """Обработка времени рождения"""
    birth_time = message.text.strip()
    if not validate_time_format(birth_time):
        await message.answer("❌ Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 14:30):")
        return

    await state.update_data(birth_time=birth_time)
    await state.set_state(NatalChartStates.waiting_birth_place)
    await message.answer("✅ Время сохранено. Теперь введите место рождения (город, страна):")

@router.message(NatalChartStates.waiting_birth_place)
async def process_birth_place(message: Message, state: FSMContext):
    """Обработка места рождения и генерация натальной карты"""
    birth_place = message.text.strip()
    if not birth_place:
        await message.answer("❌ Место рождения не может быть пустым. Пожалуйста, введите место рождения:")
        return

    user_data = await state.get_data()
    birth_date = user_data.get('birth_date')
    birth_time = user_data.get('birth_time')

    # Проверяем оплату
    if await payment_service.process_payment(message.from_user.id, "natal_chart"):
        # Логируем запрос
        db.log_request(message.from_user.id, "natal_chart")
        
        generating_msg = await message.answer(
            f"🌌 Генерирую натальную карту...\n\n"
            f"<em>Дата: {birth_date}\n"
            f"Время: {birth_time}\n"
            f"Место: {birth_place}</em>\n\n"
            "Это может занять несколько секунд."
        )
        
        try:
            natal_chart_text = await gemini_service.generate_natal_chart_interpretation({
                'birth_date': birth_date,
                'birth_time': birth_time,
                'birth_place': birth_place
            })
            
            # Разбиваем длинное сообщение на части
            header = (
                f"🌌 <b>Ваша натальная карта</b>\n\n"
                f"<b>Данные:</b>\n"
                f"📅 Дата: {birth_date}\n"
                f"⏰ Время: {birth_time}\n"
                f"📍 Место: {birth_place}\n\n"
            )
            footer = "\n\n<i>Услуга оплачена (200 звёзд)</i>"
            
            # Первая часть с заголовком
            first_part = header + natal_chart_text[:4000 - len(header + footer)] + footer
            await generating_msg.edit_text(first_part)
            
            # Если текст длинный, отправляем остальные части
            if len(natal_chart_text) > 4000:
                remaining_text = natal_chart_text[4000 - len(header + footer):]
                message_parts = split_message(remaining_text, 4000)
                
                for part in message_parts:
                    await message.answer(part)
            
        except Exception as e:
            error_text = (
                f"❌ Произошла ошибка при генерации натальной карты.\n\n"
                f"<em>Ошибка: {str(e)}</em>\n\n"
                f"Средства не были списаны."
            )
            await generating_msg.edit_text(error_text)
    else:
        await message.answer(
            "❌ <b>Недостаточно средств</b>\n\n"
            "Для использования этой услуги требуется 200 Telegram Stars.\n"
            "Пополните баланс и попробуйте снова."
        )
    
    await state.clear()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def validate_date_format(date_str):
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

def validate_time_format(time_str):
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