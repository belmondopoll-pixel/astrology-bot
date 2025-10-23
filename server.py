import logging
from aiohttp import web
import json
from database import db
from services.gemini_service import gemini_service
from services.balance_service import balance_service
from services.payment_service import payment_service
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
        self.app.router.add_route('POST', '/api/process_payment', self.handle_payment)
        self.app.router.add_route('POST', '/api/request_history', self.handle_request_history)
        
        # OPTIONS для CORS
        self.app.router.add_route('OPTIONS', '/api/user/{user_id}', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/daily_horoscope', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/weekly_horoscope', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/compatibility', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/tarot', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/natal_chart', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/process_payment', self.handle_options)
        self.app.router.add_route('OPTIONS', '/api/request_history', self.handle_options)

    def setup_middlewares(self):
        """Настройка middleware для CORS"""
        @web.middleware
        async def cors_middleware(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        self.app.middlewares.append(cors_middleware)

    async def handle_options(self, request):
        """Обработчик OPTIONS запросов для CORS"""
        return web.Response(status=200, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        })

    async def handle_user(self, request):
        """Получение данных пользователя"""
        try:
            user_id = int(request.match_info['user_id'])
            user = db.get_user(user_id)
            balance = await balance_service.get_balance(user_id)
            
            response_data = {
                "success": True,
                "user": {
                    "id": user_id,
                    "name": "Пользователь",
                    "balance": balance,
                    "is_admin": str(user_id) == str(ADMIN_ID)
                }
            }
            
            if user:
                response_data["user"].update({
                    "name": user[3] or "Пользователь",
                    "zodiac": user[6]
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
            
            cost = 333
            if str(user_id) != str(ADMIN_ID):
                if not await balance_service.can_afford(user_id, cost):
                    return web.json_response({
                        "success": False,
                        "error": f"Недостаточно средств. Нужно {cost} звезд."
                    }, status=402)
                
                if not await balance_service.update_balance(user_id, cost, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            horoscope_text = await gemini_service.generate_weekly_horoscope(zodiac_sign)
            db.log_request(user_id, f"weekly_horoscope_{zodiac_sign}")
            
            return web.json_response({
                "success": True,
                "content": horoscope_text,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else cost
            })
            
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
            
            cost = 55
            if str(user_id) != str(ADMIN_ID):
                if not await balance_service.can_afford(user_id, cost):
                    return web.json_response({
                        "success": False,
                        "error": f"Недостаточно средств. Нужно {cost} звезд."
                    }, status=402)
                
                if not await balance_service.update_balance(user_id, cost, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            compatibility_text = await gemini_service.generate_compatibility(sign1, sign2)
            db.log_request(user_id, f"compatibility_{sign1}_{sign2}")
            
            return web.json_response({
                "success": True,
                "content": compatibility_text,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else cost
            })
            
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
            
            cost = 888
            if str(user_id) != str(ADMIN_ID):
                if not await balance_service.can_afford(user_id, cost):
                    return web.json_response({
                        "success": False,
                        "error": f"Недостаточно средств. Нужно {cost} звезд."
                    }, status=402)
                
                if not await balance_service.update_balance(user_id, cost, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            cards, positions = tarot_deck.create_spread(spread_type)
            spread_description = await self.create_tarot_prompt(spread_type, cards, positions)
            interpretation = await gemini_service.generate_tarot_reading(spread_type, spread_description)
            
            formatted_cards = []
            for i, card in enumerate(cards):
                formatted_cards.append({
                    "name": card["name"],
                    "position": card["position"],
                    "meaning": tarot_deck.get_card_meaning(card)
                })
            
            db.log_request(user_id, f"tarot_{spread_type}")
            
            return web.json_response({
                "success": True,
                "cards": formatted_cards,
                "interpretation": interpretation,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else cost
            })
            
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
            
            cost = 999
            if str(user_id) != str(ADMIN_ID):
                if not await balance_service.can_afford(user_id, cost):
                    return web.json_response({
                        "success": False,
                        "error": f"Недостаточно средств. Нужно {cost} звезд."
                    }, status=402)
                
                if not await balance_service.update_balance(user_id, cost, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            natal_chart_text = await gemini_service.generate_natal_chart_interpretation(birth_data)
            db.log_request(user_id, "natal_chart")
            
            return web.json_response({
                "success": True,
                "content": natal_chart_text,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else cost
            })
            
        except Exception as e:
            logger.error(f"Error in handle_natal_chart: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_payment(self, request):
        """Обработка платежей"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            amount = data.get('amount')
            
            if await payment_service.add_funds(user_id, amount):
                return web.json_response({
                    "success": True,
                    "new_balance": await balance_service.get_balance(user_id)
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Ошибка пополнения баланса"
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error in handle_payment: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_request_history(self, request):
        """Получение истории запросов"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            
            history = db.get_user_requests(user_id, limit=10)
            
            formatted_history = []
            for req in history:
                cost = 0
                if "weekly_horoscope" in req[0]:
                    cost = 333
                elif "compatibility" in req[0]:
                    cost = 55
                elif "tarot" in req[0]:
                    cost = 888
                elif "natal_chart" in req[0]:
                    cost = 999
                
                formatted_history.append({
                    "service": req[0],
                    "date": req[1],
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

    async def create_tarot_prompt(self, spread_type, cards, positions):
        """Создание промпта для Gemini на основе выпавших карт"""
        spread_descriptions = {
            "celtic": "Кельтский крест - глубокий анализ текущей ситуации и ее развития",
            "three": "Расклад на три карты: Прошлое, Настоящее, Будущее",
            "four": "Расклад на четыре карты: Ситуация, Вызовы, Совет, Результат", 
            "daily": "Карта дня - совет на сегодняшний день"
        }
        
        prompt = f"Проинтерпретируй расклад Таро: {spread_descriptions.get(spread_type, spread_type)}\n\nВыпавшие карты и их позиции:"
        
        for i, card in enumerate(cards):
            position = positions[i] if i < len(positions) else f"Позиция {i+1}"
            orientation = "прямое" if card["position"] == "upright" else "перевернутое"
            meaning = tarot_deck.get_card_meaning(card)
            prompt += f"\n- {position}: {card['name']} ({orientation} положение) - {meaning}"
        
        prompt += """
        \n\nПроанализируй:
        1. Общую энергетику расклада
        2. Значение каждой карты в ее позиции
        3. Взаимосвязи между картами
        4. Практические рекомендации
        5. Потенциальные развития ситуации
        
        Будь мудрым и поддерживающим. Избегай категоричных предсказаний.
        Объем: 300-400 слов. На русском языке.
        """
        
        return prompt

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