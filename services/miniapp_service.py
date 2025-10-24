# services/miniapp_service.py
import logging
from typing import Dict, Any
from database import db
from services.direct_payment_service import direct_payment_service
from config import ADMIN_ID

logger = logging.getLogger(__name__)

class MiniAppService:
    def __init__(self):
        self.service_costs = {
            "daily_horoscope": 0,
            "weekly_horoscope": 333,
            "compatibility": 55,
            "tarot": 888,
            "natal": 999
        }

    async def process_miniapp_request(self, user_id: int, service_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка запроса из MiniApp"""
        try:
            # Для администратора - всегда успех
            if str(user_id) == str(ADMIN_ID):
                return {
                    "success": True,
                    "message": "Запрос обработан (демо-режим)",
                    "cost": 0,
                    "demo_mode": True
                }
            
            # Для обычных пользователей - требуется оплата
            return {
                "success": True,
                "message": "Требуется оплата услуги",
                "cost": self.service_costs.get(service_type, 0),
                "payment_required": True
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки запроса MiniApp: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Получение данных пользователя для MiniApp"""
        try:
            user = db.get_user(user_id)
            
            user_data = {
                "id": user_id,
                "name": "Пользователь",
                "is_admin": str(user_id) == str(ADMIN_ID)
            }
            
            if user:
                user_data.update({
                    "name": user[3] or "Пользователь",
                    "zodiac": user[6] or "Не указан"
                })
            
            return user_data
            
        except Exception as e:
            logger.error(f"Ошибка получения данных пользователя: {e}")
            return {
                "id": user_id,
                "name": "Пользователь",
                "is_admin": False
            }

miniapp_service = MiniAppService()