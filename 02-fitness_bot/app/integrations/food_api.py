from typing import List, Dict
import aiohttp
from app.utils.exceptions import APIError


class FoodAPI:
    def __init__(self):
        self.base_url = "https://world.openfoodfacts.org/cgi/search.pl"

    async def search_food(self, query: str) -> List[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'search_terms': query,
                    'search_simple': 1,
                    'action': 'process',
                    'json': 1,
                    'page_size': 5  # Ограничиваем количество результатов
                }

                async with session.get(self.base_url, params=params) as response:  # noqa E501
                    if response.status != 200:
                        raise APIError(f"API request failed with status {
                                       response.status}")

                    data = await response.json()
                    products = data.get('products', [])

                    if not products:
                        return []

                    result = []
                    for product in products:
                        # Получаем питательные вещества
                        nutrients = product.get('nutriments', {})

                        # Проверяем наличие основных данных
                        if not product.get('product_name'):
                            continue

                        # Формируем информацию о продукте
                        food_item = {
                            'name': product.get('product_name'),
                            'calories': nutrients.get('energy-kcal_100g', 0),
                            'serving_size': 100,  # Стандартная порция 100г
                            'proteins': nutrients.get('proteins_100g', 0),
                            'fats': nutrients.get('fat_100g', 0),
                            'carbs': nutrients.get('carbohydrates_100g', 0)
                        }

                        # Проверяем наличие калорий
                        if food_item['calories']:
                            result.append(food_item)

                    return result

        except aiohttp.ClientError as e:
            raise APIError(f"Network error occurred: {str(e)}")
        except Exception as e:
            raise APIError(f"Error searching food: {str(e)}")
