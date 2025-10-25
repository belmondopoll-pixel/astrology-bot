# handlers/payment_handlers.py
from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery, SuccessfulPayment
from aiogram.filters import Command
import logging

from database import db
from services.stars_payment_service import stars_payment_service
from services.gemini_service import gemini_service
from services.tarot_deck import tarot_deck

logger = logging.getLogger(__name__)

router = Router()

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Обработчик предварительного запроса на оплату"""
    try:
        # Всегда подтверждаем pre-checkout для Telegram Stars
        await pre_checkout_query.answer(ok=True)
        logger.info(f"✅ Pre-checkout запрос подтвержден: {pre_checkout_query.id}")
    except Exception as e:
        logger.error(f"❌ Ошибка pre-checkout: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Ошибка обработки платежа")

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Обработчик успешного платежа"""
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        
        logger.info(f"💰 Успешный платеж: {payment.total_amount} Stars от пользователя {user_id}")
        
        # Обрабатываем платеж в сервисе
        success = await stars_payment_service.process_successful_payment(
            user_id, 
            payment.invoice_payload, 
            payment.total_amount
        )
        
        if success:
            # Предоставляем услугу в зависимости от типа
            await provide_paid_service(user_id, payment.invoice_payload, message)
        else:
            await message.answer("❌ Ошибка при обработке платежа. Обратитесь в поддержку.")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки успешного платежа: {e}")
        await message.answer("❌ Произошла ошибка. Обратитесь в поддержку.")

async def provide_paid_service(user_id: int, payload: str, message: Message):
    """Предоставление оплаченной услуги"""
    try:
        parts = payload.split("_")
        service_type = parts[0]
        
        if service_type == "compatibility":
            if len(parts) >= 3:
                sign1 = parts[1]
                sign2 = parts[2]
                compatibility_text = await gemini_service.generate_compatibility(sign1, sign2)
                
                await message.answer(
                    f"💑 <b>Совместимость: {sign1} и {sign2}</b>\n\n"
                    f"{compatibility_text}\n\n"
                    f"<i>✅ Услуга оплачена • 55 Stars</i>"
                )
                
        elif service_type == "weekly_horoscope":
            if len(parts) >= 2:
                zodiac_sign = parts[1]
                horoscope_text = await gemini_service.generate_weekly_horoscope(zodiac_sign)
                
                await message.answer(
                    f"📅 <b>Гороскоп на неделю для {zodiac_sign}</b>\n\n"
                    f"{horoscope_text}\n\n"
                    f"<i>✅ Услуга оплачена • 333 Stars</i>"
                )
                
        elif service_type == "tarot":
            if len(parts) >= 2:
                spread_type = parts[1]
                
                spread_names = {
                    "celtic": "Кельтский крест",
                    "three": "Прошлое-Настоящее-Будущее", 
                    "four": "Ситуация-Вызовы-Совет-Результат",
                    "daily": "Карта дня"
                }
                
                spread_name = spread_names.get(spread_type, "Выбранный расклад")
                
                cards, positions = tarot_deck.create_spread(spread_type)
                
                # Форматируем результат
                cards_text = "🎴 Ваш расклад:\n\n"
                for i, card in enumerate(cards):
                    position_name = positions[i] if i < len(positions) else f"Позиция {i+1}"
                    orientation = "🔼" if card["position"] == "upright" else "🔽"
                    cards_text += f"{orientation} <b>{position_name}:</b>\n"
                    cards_text += f"   🃏 {card['name']}\n"
                    cards_text += f"   📖 {tarot_deck.get_card_meaning(card)}\n\n"
                
                interpretation = await gemini_service.generate_tarot_reading(spread_type, "")
                
                full_content = f"{cards_text}\n💫 <b>Интерпретация:</b>\n\n{interpretation}"
                
                await message.answer(
                    f"🃏 <b>{spread_name}</b>\n\n"
                    f"{full_content}\n\n"
                    f"<i>✅ Услуга оплачена • 888 Stars</i>"
                )
                
        elif service_type == "natal":
            # Для натальной карты нужно получить данные из базы или запросить заново
            natal_chart_text = await gemini_service.generate_natal_chart_interpretation({})
            
            await message.answer(
                f"🌌 <b>Ваша натальная карта</b>\n\n"
                f"{natal_chart_text}\n\n"
                f"<i>✅ Услуга оплачена • 999 Stars</i>"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка предоставления услуги: {e}")
        await message.answer("❌ Ошибка при предоставлении услуги. Обратитесь в поддержку.")

@router.message(Command("balance"))
async def check_balance(message: Message):
    """Проверка баланса Stars"""
    # В реальном боте можно показывать баланс Stars из Telegram
    await message.answer(
        f"💰 <b>Ваш баланс Telegram Stars</b>\n\n"
        f"Для просмотра баланса Stars откройте:\n"
        f"• Настройки Telegram → Telegram Stars\n"
        f"• Или проверьте в любом чате через меню\n\n"
        f"💡 Stars можно получить от подписчиков или купить в Telegram"
    )