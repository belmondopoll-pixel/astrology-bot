# api/server.py
import logging
from aiohttp import web
import json
from database import db
from services.gemini_service import gemini_service
from services.tarot_deck import tarot_deck
from config import ADMIN_ID

logger = logging.getLogger(__name__)

class MiniAppAPI:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.setup_middlewares()

    def setup_routes(self):
        """Настройка маршрутов API"""
        # Основные маршруты
        self.app.router.add_route('POST', '/api/user/{user_id}', self.handle_user)
        self.app.router.add_route('POST', '/api/daily_horoscope', self.handle_daily_horoscope)
        self.app.router.add_route('POST', '/api/weekly_horoscope', self.handle_weekly_horoscope)
        self.app.router.add_route('POST', '/api/compatibility', self.handle_compatibility)
        self.app.router.add_route('POST', '/api/tarot', self.handle_tarot)
        self.app.router.add_route('POST', '/api/natal_chart', self.handle_natal_chart)
        self.app.router.add_route('POST', '/api/request_history', self.handle_request_history)
        self.app.router.add_route('POST', '/api/check_payment', self.handle_check_payment)
        self.app.router.add_route('POST', '/api/confirm_payment', self.handle_confirm_payment)
        
        # OPTIONS для CORS
        self.app.router.add_route('OPTIONS', '/api/user/{user_id}', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/daily_horoscope', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/weekly_horoscope', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/compatibility', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/tarot', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/natal_chart', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/request_history', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/check_payment', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/confirm_payment', self.handle_options)

    def setup_middlewares(self):
        """Настройка middleware для CORS"""
        @web.middleware
        async def cors_middleware(request, handler):
            if request.method == 'OPTIONS':
                response = web.Response()
            else:
                response = await handler(request)
            
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT, DELETE'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        self.app.middlewares.append(cors_middleware)

    async def handle_options(self, request):
        """Обработчик OPTIONS запросов для CORS"""
        return web.Response(status=200, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Allow-Credentials': 'true'
        })

    async def handle_user(self, request):
        """Получение данных пользователя"""
        try:
            user_id = int(request.match_info['user_id'])
            user = db.get_user(user_id)
            user_balance = db.get_user_balance(user_id) if user else 100
            
            response_data = {
                "success": True,
                "user": {
                    "id": user_id,
                    "name": "Пользователь",
                    "balance": user_balance,
                    "is_admin": str(user_id) == str(ADMIN_ID)
                }
            }
            
            if user:
                response_data["user"].update({
                    "name": user[3] or "Пользователь",
                    "zodiac": user[6] or "Не указан"
                })
            
            return web.json_response(response_data)
            
        except Exception as e:
            logger.error(f"Error in handle_user: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_daily_horoscope(self, request):
        """Обработка ежедневного гороскопа"""
        try:
            data = await request.json()
            zodiac_sign = data.get('zodiac_sign')
            user_id = data.get('user_id')
            
            if not zodiac_sign:
                return web.json_response({
                    "success": False,
                    "error": "Не указан знак зодиака"
                }, status=400)
            
            horoscope_text = await gemini_service.safe_generate_horoscope(zodiac_sign)
            db.log_request(user_id, f"daily_horoscope_{zodiac_sign}")
            
            return web.json_response({
                "success": True,
                "content": horoscope_text,
                "cost": 0
            })
            
        except Exception as e:
            logger.error(f"Error in handle_daily_horoscope: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_weekly_horoscope(self, request):
        """Обработка недельного гороскопа"""
        try:
            data = await request.json()
            zodiac_sign = data.get('zodiac_sign')
            user_id = data.get('user_id')
            
            if not zodiac_sign:
                return web.json_response({
                    "success": False,
                    "error": "Не указан знак зодиака"
                }, status=400)
            
            # Проверяем баланс пользователя
            cost = 333
            user_balance = db.get_user_balance(user_id)
            
            if user_balance < cost:
                return web.json_response({
                    "success": False,
                    "error": f"Недостаточно средств. Нужно {cost} Stars, у вас {user_balance} Stars.",
                    "payment_required": True,
                    "cost": cost
                }, status=402)
            
            # Списываем средства
            if db.update_balance(user_id, -cost):
                horoscope_text = await gemini_service.generate_weekly_horoscope(zodiac_sign)
                db.log_request(user_id, f"weekly_horoscope_{zodiac_sign}", cost)
                
                return web.json_response({
                    "success": True,
                    "content": horoscope_text,
                    "cost": cost
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Ошибка списания средств"
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error in handle_weekly_horoscope: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_compatibility(self, request):
        """Обработка совместимости"""
        try:
            data = await request.json()
            sign1 = data.get('sign1')
            sign2 = data.get('sign2')
            user_id = data.get('user_id')
            
            if not sign1 or not sign2:
                return web.json_response({
                    "success": False,
                    "error": "Не указаны знаки зодиака"
                }, status=400)
            
            # Проверяем баланс пользователя
            cost = 55
            user_balance = db.get_user_balance(user_id)
            
            if user_balance < cost:
                return web.json_response({
                    "success": False,
                    "error": f"Недостаточно средств. Нужно {cost} Stars, у вас {user_balance} Stars.",
                    "payment_required": True,
                    "cost": cost
                }, status=402)
            
            # Списываем средства
            if db.update_balance(user_id, -cost):
                compatibility_text = await gemini_service.generate_compatibility(sign1, sign2)
                db.log_request(user_id, f"compatibility_{sign1}_{sign2}", cost)
                
                return web.json_response({
                    "success": True,
                    "content": compatibility_text,
                    "cost": cost
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Ошибка списания средств"
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error in handle_compatibility: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_tarot(self, request):
        """Обработка расклада Таро"""
        try:
            data = await request.json()
            spread_type = data.get('spread_type')
            user_id = data.get('user_id')
            
            if not spread_type:
                return web.json_response({
                    "success": False,
                    "error": "Не указан тип расклада"
                }, status=400)
            
            # Проверяем баланс пользователя
            cost = 888
            user_balance = db.get_user_balance(user_id)
            
            if user_balance < cost:
                return web.json_response({
                    "success": False,
                    "error": f"Недостаточно средств. Нужно {cost} Stars, у вас {user_balance} Stars.",
                    "payment_required": True,
                    "cost": cost
                }, status=402)
            
            # Списываем средства
            if db.update_balance(user_id, -cost):
                cards, positions = tarot_deck.create_spread(spread_type)
                
                spread_description = ""
                for i, card in enumerate(cards):
                    position_name = positions[i] if i < len(positions) else f"Позиция {i+1}"
                    orientation = "прямое" if card["position"] == "upright" else "перевернутое"
                    spread_description += f"{position_name}: {card['name']} ({orientation})\n"
                
                interpretation = await gemini_service.generate_tarot_reading(spread_type, spread_description)
                
                formatted_cards = []
                for i, card in enumerate(cards):
                    formatted_cards.append({
                        "name": card["name"],
                        "position": card["position"],
                        "meaning": tarot_deck.get_card_meaning(card),
                        "position_name": positions[i] if i < len(positions) else f"Позиция {i+1}"
                    })
                
                db.log_request(user_id, f"tarot_{spread_type}", cost)
                
                return web.json_response({
                    "success": True,
                    "cards": formatted_cards,
                    "interpretation": interpretation,
                    "cost": cost
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Ошибка списания средств"
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error in handle_tarot: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_natal_chart(self, request):
        """Обработка натальной карты"""
        try:
            data = await request.json()
            birth_data = data.get('birth_data', {})
            user_id = data.get('user_id')
            
            required_fields = ['birth_date', 'birth_time', 'birth_place']
            for field in required_fields:
                if not birth_data.get(field):
                    return web.json_response({
                        "success": False,
                        "error": f"Не указано поле: {field}"
                    }, status=400)
            
            # Проверяем баланс пользователя
            cost = 999
            user_balance = db.get_user_balance(user_id)
            
            if user_balance < cost:
                return web.json_response({
                    "success": False,
                    "error": f"Недостаточно средств. Нужно {cost} Stars, у вас {user_balance} Stars.",
                    "payment_required": True,
                    "cost": cost
                }, status=402)
            
            # Списываем средства
            if db.update_balance(user_id, -cost):
                natal_chart_text = await gemini_service.generate_natal_chart_interpretation(birth_data)
                db.log_request(user_id, "natal_chart", cost)
                
                return web.json_response({
                    "success": True,
                    "content": natal_chart_text,
                    "cost": cost
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Ошибка списания средств"
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error in handle_natal_chart: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_check_payment(self, request):
        """Проверка возможности оплаты услуги"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            service_type = data.get('service_type')
            
            service_costs = {
                'weekly_horoscope': 333,
                'compatibility': 55,
                'tarot': 888,
                'natal_chart': 999
            }
            
            cost = service_costs.get(service_type, 0)
            user_balance = db.get_user_balance(user_id)
            
            can_afford = user_balance >= cost
            
            return web.json_response({
                "success": True,
                "can_afford": can_afford,
                "user_balance": user_balance,
                "service_cost": cost,
                "remaining_balance": user_balance - cost if can_afford else user_balance
            })
            
        except Exception as e:
            logger.error(f"Error in handle_check_payment: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_confirm_payment(self, request):
        """Подтверждение оплаты и предоставление услуги"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            service_type = data.get('service_type')
            service_data = data.get('service_data', {})
            
            service_costs = {
                'weekly_horoscope': 333,
                'compatibility': 55,
                'tarot': 888,
                'natal_chart': 999
            }
            
            cost = service_costs.get(service_type, 0)
            user_balance = db.get_user_balance(user_id)
            
            if user_balance < cost:
                return web.json_response({
                    "success": False,
                    "error": f"Недостаточно средств. Нужно {cost} Stars, у вас {user_balance} Stars."
                }, status=402)
            
            # Списываем средства
            if not db.update_balance(user_id, -cost):
                return web.json_response({
                    "success": False,
                    "error": "Ошибка списания средств"
                }, status=500)
            
            # Предоставляем услугу
            result = await self.provide_service(service_type, service_data, user_id)
            
            if result["success"]:
                # Логируем запрос
                if service_type == 'compatibility':
                    sign1 = service_data.get('sign1', '')
                    sign2 = service_data.get('sign2', '')
                    db.log_request(user_id, f"compatibility_{sign1}_{sign2}", cost)
                elif service_type == 'weekly_horoscope':
                    zodiac_sign = service_data.get('zodiac_sign', '')
                    db.log_request(user_id, f"weekly_horoscope_{zodiac_sign}", cost)
                elif service_type == 'tarot':
                    spread_type = service_data.get('spread_type', '')
                    db.log_request(user_id, f"tarot_{spread_type}", cost)
                elif service_type == 'natal_chart':
                    db.log_request(user_id, "natal_chart", cost)
                
                result["cost"] = cost
                result["new_balance"] = db.get_user_balance(user_id)
                return web.json_response(result)
            else:
                # Возвращаем средства при ошибке
                db.update_balance(user_id, cost)
                return web.json_response({
                    "success": False,
                    "error": result.get("error", "Ошибка предоставления услуги")
                }, status=500)
                    
        except Exception as e:
            logger.error(f"Error in handle_confirm_payment: {e}")
            # Возвращаем средства при исключении
            db.update_balance(user_id, cost)
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def provide_service(self, service_type: str, service_data: dict, user_id: int):
        """Предоставление оплаченной услуги"""
        try:
            if service_type == 'compatibility':
                sign1 = service_data.get('sign1')
                sign2 = service_data.get('sign2')
                if not sign1 or not sign2:
                    return {"success": False, "error": "Не указаны знаки зодиака"}
                
                content = await gemini_service.generate_compatibility(sign1, sign2)
                return {
                    "success": True,
                    "content": content,
                    "service_type": "compatibility"
                }
                
            elif service_type == 'weekly_horoscope':
                zodiac_sign = service_data.get('zodiac_sign')
                if not zodiac_sign:
                    return {"success": False, "error": "Не указан знак зодиака"}
                
                content = await gemini_service.generate_weekly_horoscope(zodiac_sign)
                return {
                    "success": True,
                    "content": content,
                    "service_type": "weekly_horoscope"
                }
                
            elif service_type == 'tarot':
                spread_type = service_data.get('spread_type', 'daily')
                cards, positions = tarot_deck.create_spread(spread_type)
                
                spread_description = ""
                for i, card in enumerate(cards):
                    position_name = positions[i] if i < len(positions) else f"Позиция {i+1}"
                    orientation = "прямое" if card["position"] == "upright" else "перевернутое"
                    spread_description += f"{position_name}: {card['name']} ({orientation})\n"
                
                interpretation = await gemini_service.generate_tarot_reading(spread_type, spread_description)
                
                formatted_cards = []
                for i, card in enumerate(cards):
                    formatted_cards.append({
                        "name": card["name"],
                        "position": card["position"],
                        "meaning": tarot_deck.get_card_meaning(card),
                        "position_name": positions[i] if i < len(positions) else f"Позиция {i+1}"
                    })
                
                return {
                    "success": True,
                    "cards": formatted_cards,
                    "interpretation": interpretation,
                    "service_type": "tarot"
                }
                
            elif service_type == 'natal_chart':
                birth_data = service_data.get('birth_data', {})
                required_fields = ['birth_date', 'birth_time', 'birth_place']
                for field in required_fields:
                    if not birth_data.get(field):
                        return {"success": False, "error": f"Не указано поле: {field}"}
                
                content = await gemini_service.generate_natal_chart_interpretation(birth_data)
                return {
                    "success": True,
                    "content": content,
                    "service_type": "natal_chart"
                }
                
            else:
                return {"success": False, "error": f"Неизвестный тип услуги: {service_type}"}
                
        except Exception as e:
            logger.error(f"Error in provide_service: {e}")
            return {"success": False, "error": str(e)}

    async def handle_request_history(self, request):
        """Получение истории запросов"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            
            history = db.get_user_requests(user_id, limit=10)
            
            formatted_history = []
            for req in history:
                service_type = req[0]
                date = req[1]
                cost = req[2] if len(req) > 2 else 0
                
                formatted_history.append({
                    "service": service_type,
                    "date": date,
                    "cost": cost
                })
            
            return web.json_response({
                "success": True,
                "history": formatted_history
            })
            
        except Exception as e:
            logger.error(f"Error in handle_request_history: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def start(self):
        """Запуск API сервера"""
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8080)
            await site.start()
            logger.info("✅ API сервер запущен на порту 8080")
        except Exception as e:
            logger.error(f"❌ Ошибка запуска API сервера: {e}")

# Создаем экземпляр API
miniapp_api = MiniAppAPI()