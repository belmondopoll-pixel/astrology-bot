import logging
import json
from typing import Dict, Any
from database import db
from services.balance_service import balance_service
from config import ADMIN_ID

logger = logging.getLogger(__name__)

class MiniAppService:
    def __init__(self):
        self.service_costs = {
            "daily_horoscope": 0,
            "weekly_horoscope": 333,  # было 100
            "compatibility": 55,      # было 50
            "tarot": 888,             # было 80
            "natal": 999              # было 200
        }

    async def process_miniapp_request(self, user_id: int, service_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка запроса из MiniApp"""
        try:
            cost = self.service_costs.get(service_type, 0)
            
            # Для администратора все услуги бесплатны
            if cost > 0 and str(user_id) != str(ADMIN_ID):
                can_afford = await balance_service.can_afford(user_id, cost)
                if not can_afford:
                    return {
                        "success": False,
                        "error": f"Недостаточно средств. Нужно {cost} звезд."
                    }
                
                # Списание средств
                if not await balance_service.update_balance(user_id, cost, "subtract"):
                    return {
                        "success": False,
                        "error": "Ошибка списания средств"
                    }
            
            # Логируем запрос
            db.log_request(user_id, f"miniapp_{service_type}")
            
            return {
                "success": True,
                "message": "Запрос обработан",
                "cost": 0 if str(user_id) == str(ADMIN_ID) else cost,
                "new_balance": await balance_service.get_balance(user_id)
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
            balance = await balance_service.get_balance(user_id)
            
            if user:
                return {
                    "id": user[1],
                    "name": user[3] or "Пользователь",
                    "zodiac": user[6],
                    "balance": balance,
                    "is_admin": str(user_id) == str(ADMIN_ID)
                }
            return {
                "id": user_id,
                "name": "Пользователь",
                "balance": balance,
                "is_admin": str(user_id) == str(ADMIN_ID)
            }
        except Exception as e:
            logger.error(f"Ошибка получения данных пользователя: {e}")
            return {
                "id": user_id,
                "name": "Пользователь",
                "balance": 0,
                "is_admin": False
            }

miniapp_service = MiniAppService()