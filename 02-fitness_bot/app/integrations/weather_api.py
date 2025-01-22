import aiohttp

from config import settings
from app.utils.exceptions import ExternalServiceError


class WeatherAPI:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    async def get_temperature(self, city: str) -> float:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': city,
                    'appid': self.api_key,
                    'units': 'metric'
                }

                async with session.get(self.base_url, params=params) as response:  # noqa E501
                    if response.status != 200:
                        error_text = await response.text()
                        raise ExternalServiceError(
                            f"Не удалось получить температуру: {error_text}"
                        )

                    data = await response.json()
                    return data['main']['temp']

        except aiohttp.ClientError as e:
            raise ExternalServiceError(f"Ошибка соединения с API: {str(e)}")
        except KeyError as e:
            raise ExternalServiceError(
                f"Неверный формат ответа от API: {str(e)}")
        except Exception as e:
            raise ExternalServiceError(f"Неизвестная ошибка: {str(e)}")

    async def close(self):
        """Метод для корректного закрытия сессии"""
        if hasattr(self, 'session'):
            await self.session.close()
