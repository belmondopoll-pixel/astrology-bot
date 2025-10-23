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
        # Основные маршруты API
        self.app.router.add_post('/api/user/{user_id}', self.handle_user)
        self.app.router.add_post('/api/daily_horoscope', self.handle_daily_horoscope)
        self.app.router.add_post('/api/weekly_horoscope', self.handle_weekly_horoscope)
        self.app.router.add_post('/api/compatibility', self.handle_compatibility)
        self.app.router.add_post('/api/tarot', self.handle_tarot)
        self.app.router.add_post('/api/natal_chart', self.handle_natal_chart)
        self.app.router.add_post('/api/process_payment', self.handle_payment)
        self.app.router.add_post('/api/request_history', self.handle_request_history)
        
        # OPTIONS для CORS preflight - явно указываем пути
        routes_to_handle = [
            '/api/user/{user_id}',
            '/api/daily_horoscope',
            '/api/weekly_horoscope', 
            '/api/compatibility',
            '/api/tarot',
            '/api/natal_chart',
            '/api/process_payment',
            '/api/request_history'
        ]
        
        for route_path in routes_to_handle:
            self.app.router.add_route('OPTIONS', route_path, self.handle_options)

    def setup_middlewares(self):
        # CORS middleware
        @web.middleware
        async def cors_middleware(request, handler):
            if request.method == 'OPTIONS':
                response = web.Response()
            else:
                response = await handler(request)
            
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '86400'
            return response
        
        self.app.middlewares.append(cors_middleware)

    async def handle_options(self, request):
        return web.Response(status=200)

    # Остальные методы оставляем без изменений...
    async def handle_user(self, request):
        """Получение данных пользователя"""
        try:
            user_id = int(request.match_info['user_id'])
            user = db.get_user(user_id)
            balance = await balance_service.get_balance(user_id)
            
            if user:
                user_data = {
                    "success": True,
                    "user": {
                        "id": user[1],
                        "name": user[3] or "Пользователь",
                        "zodiac": user[6],
                        "balance": balance,
                        "is_admin": str(user_id) == str(ADMIN_ID)
                    }
                }
            else:
                user_data = {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "name": "Пользователь",
                        "balance": balance,
                        "is_admin": str(user_id) == str(ADMIN_ID)
                    }
                }
            
            return web.json_response(user_data)
            
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
            
            # Генерируем гороскоп через Gemini
            horoscope_text = await gemini_service.safe_generate_horoscope(zodiac_sign)
            
            # Логируем запрос
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
            
            # Для администратора услуга бесплатна
            if str(user_id) != str(ADMIN_ID):
                # Проверяем баланс
                if not await balance_service.can_afford(user_id, 333):
                    return web.json_response({
                        "success": False,
                        "error": "Недостаточно средств. Нужно 333 звезды."
                    }, status=402)
                
                # Списание средств
                if not await balance_service.update_balance(user_id, 333, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            # Генерируем гороскоп
            horoscope_text = await gemini_service.generate_weekly_horoscope(zodiac_sign)
            
            # Логируем запрос
            db.log_request(user_id, f"weekly_horoscope_{zodiac_sign}")
            
            return web.json_response({
                "success": True,
                "content": horoscope_text,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else 333
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
            
            # Для администратора услуга бесплатна
            if str(user_id) != str(ADMIN_ID):
                # Проверяем баланс
                if not await balance_service.can_afford(user_id, 55):
                    return web.json_response({
                        "success": False,
                        "error": "Недостаточно средств. Нужно 55 звезд."
                    }, status=402)
                
                # Списание средств
                if not await balance_service.update_balance(user_id, 55, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            # Генерируем совместимость
            compatibility_text = await gemini_service.generate_compatibility(sign1, sign2)
            
            # Логируем запрос
            db.log_request(user_id, f"compatibility_{sign1}_{sign2}")
            
            return web.json_response({
                "success": True,
                "content": compatibility_text,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else 55
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
            
            # Для администратора услуга бесплатна
            if str(user_id) != str(ADMIN_ID):
                # Проверяем баланс
                if not await balance_service.can_afford(user_id, 888):
                    return web.json_response({
                        "success": False,
                        "error": "Недостаточно средств. Нужно 888 звезд."
                    }, status=402)
                
                # Списание средств
                if not await balance_service.update_balance(user_id, 888, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            # Создаем расклад
            cards, positions = tarot_deck.create_spread(spread_type)
            
            # Генерируем интерпретацию
            spread_description = await self.create_tarot_prompt(spread_type, cards, positions)
            interpretation = await gemini_service.generate_tarot_reading(spread_type, spread_description)
            
            # Форматируем карты для ответа
            formatted_cards = []
            for i, card in enumerate(cards):
                formatted_cards.append({
                    "name": card["name"],
                    "position": card["position"],
                    "meaning": tarot_deck.get_card_meaning(card)
                })
            
            # Логируем запрос
            db.log_request(user_id, f"tarot_{spread_type}")
            
            return web.json_response({
                "success": True,
                "cards": formatted_cards,
                "interpretation": interpretation,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else 888
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
            
            # Для администратора услуга бесплатна
            if str(user_id) != str(ADMIN_ID):
                # Проверяем баланс
                if not await balance_service.can_afford(user_id, 999):
                    return web.json_response({
                        "success": False,
                        "error": "Недостаточно средств. Нужно 999 звезд."
                    }, status=402)
                
                # Списание средств
                if not await balance_service.update_balance(user_id, 999, "subtract"):
                    return web.json_response({
                        "success": False,
                        "error": "Ошибка списания средств"
                    }, status=500)
            
            # Генерируем натальную карту
            natal_chart_text = await gemini_service.generate_natal_chart_interpretation(birth_data)
            
            # Логируем запрос
            db.log_request(user_id, "natal_chart")
            
            return web.json_response({
                "success": True,
                "content": natal_chart_text,
                "cost": 0 if str(user_id) == str(ADMIN_ID) else 999
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
                formatted_history.append({
                    "service": req[0],
                    "date": req[1],
                    "cost": self._get_service_cost(req[0])
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

    def _get_service_cost(self, service_type: str):
        """Получение стоимости услуги"""
        costs = {
            "daily_horoscope": 0,
            "weekly_horoscope": 333,
            "compatibility": 55,
            "tarot": 888,
            "natal_chart": 999
        }
        
        for service, cost in costs.items():
            if service in service_type:
                return cost
        return 0

    async def create_tarot_prompt(self, spread_type: str, cards: list, positions: list):
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
            meaning = tarot_deck.get_card_meaning(card)
            prompt += f"\n- {position}: {card['name']} ({orientation} положение) - {meaning}"
        
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

    async def start(self):
        """Запуск API сервера"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logger.info("✅ API сервер запущен на порту 8080")

miniapp_api = MiniAppAPI()