# paid_services.py - ОБНОВЛЕННАЯ ВЕРСИЯ
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, SuccessfulPayment
from aiogram.fsm.context import FSMContext
import logging

from database import db
from keyboards import zodiac_keyboard, tarot_spreads_keyboard, main_menu
from services.gemini_service import gemini_service
from services.stars_payment_service import stars_payment_service

logger = logging.getLogger(__name__)

router = Router()

# ==================== ОБРАБОТЧИКИ ПЛАТЕЖЕЙ ====================

@router.message(F.text == "💑 Совместимость (55 Stars)")
async def compatibility_handler(message: Message, state: FSMContext):
    """Обработчик совместимости с созданием инвойса"""
    try:
        user_id = message.from_user.id
        
        # Создаем инвойс
        invoice = stars_payment_service.get_invoice("compatibility")
        
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title=invoice["title"],
            description=invoice["description"],
            payload=invoice["payload"],
            provider_token="",  # Для Stars не требуется
            currency=invoice["currency"],
            prices=invoice["prices"],
            start_parameter=invoice["start_parameter"]
        )
        
        await state.update_data(service_type="compatibility")
        
    except Exception as e:
        logger.error(f"Ошибка в compatibility_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "📅 Гороскоп на неделю (333 Stars)")
async def weekly_horoscope_handler(message: Message, state: FSMContext):
    """Обработчик недельного гороскопа с созданием инвойса"""
    try:
        user_id = message.from_user.id
        
        await message.answer(
            "📅 <b>Расширенный гороскоп на неделю</b>\n\n"
            "Выберите ваш знак зодиака для создания платежа:",
            reply_markup=zodiac_keyboard("weekly_invoice")
        )
            
        await state.update_data(service_type="weekly_horoscope")
        
    except Exception as e:
        logger.error(f"Ошибка в weekly_horoscope_handler: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("weekly_invoice_"))
async def create_weekly_invoice(callback: CallbackQuery, state: FSMContext):
    """Создание инвойса для недельного гороскопа"""
    try:
        await callback.answer()
        
        zodiac_sign = callback.data.split("_")[2]
        user_data = {"zodiac_sign": zodiac_sign}
        
        # Создаем инвойс
        invoice = stars_payment_service.get_invoice("weekly_horoscope", user_data)
        
        await callback.message.bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=invoice["title"],
            description=f"{invoice['description']} для {zodiac_sign}",
            payload=invoice["payload"],
            provider_token="",
            currency=invoice["currency"],
            prices=invoice["prices"],
            start_parameter=invoice["start_parameter"]
        )
        
    except Exception as e:
        logger.error(f"Ошибка в create_weekly_invoice: {e}")
        await callback.message.answer("❌ Ошибка создания платежа")

# Аналогично обновите обработчики для Таро и натальной карты...

# ==================== ОБРАБОТЧИКИ ПЛАТЕЖНЫХ СОБЫТИЙ ====================

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Обработка предварительного запроса платежа"""
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    """Обработка успешного платежа"""
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        
        # Обрабатываем платеж
        success = await stars_payment_service.process_successful_payment(
            user_id, payment.invoice_payload, payment.total_amount
        )
        
        if success:
            # Предоставляем услугу
            await provide_paid_service(user_id, payment.invoice_payload, message, state)
        else:
            await message.answer("❌ Ошибка обработки платежа. Обратитесь в поддержку.")
            
    except Exception as e:
        logger.error(f"Ошибка в successful_payment_handler: {e}")
        await message.answer("❌ Произошла ошибка при обработке платежа.")

async def provide_paid_service(user_id: int, payload: str, message: Message, state: FSMContext):
    """Предоставление оплаченной услуги"""
    try:
        parts = payload.split("_")
        service_type = parts[0]
        
        if service_type == "compatibility":
            # Запрашиваем знаки зодиака
            await message.answer(
                "💑 <b>Анализ совместимости</b>\n\n"
                "Выберите первый знак зодиака:",
                reply_markup=zodiac_keyboard("comp_first")
            )
        elif service_type == "weekly_horoscope":
            zodiac_sign = parts[1] if len(parts) > 1 else None
            if zodiac_sign:
                await generate_weekly_horoscope(message, zodiac_sign)
            else:
                await message.answer(
                    "Выберите знак зодиака:",
                    reply_markup=zodiac_keyboard("weekly_paid")
                )
        # ... аналогично для других услуг
        
    except Exception as e:
        logger.error(f"Ошибка предоставления услуги: {e}")
        await message.answer("❌ Ошибка предоставления услуги.")

async def generate_weekly_horoscope(message: Message, zodiac_sign: str):
    """Генерация недельного гороскопа после оплаты"""
    generating_msg = await message.answer(
        f"📅 <b>Генерирую гороскоп на неделю для {zodiac_sign}...</b>\n\n"
        f"<em>Это может занять несколько секунд</em>"
    )
    
    try:
        horoscope_text = await gemini_service.generate_weekly_horoscope(zodiac_sign)
        
        await generating_msg.edit_text(
            f"📅 <b>Гороскоп на неделю для {zodiac_sign}</b>\n\n"
            f"{horoscope_text}\n\n"
            f"<i>✅ Услуга оплачена • 333 Stars</i>"
        )
        
        # Логируем запрос
        db.log_request(message.from_user.id, f"weekly_horoscope_{zodiac_sign}", 333)
        
    except Exception as e:
        logger.error(f"Ошибка генерации гороскопа: {e}")
        await generating_msg.edit_text("❌ Ошибка генерации гороскопа.")