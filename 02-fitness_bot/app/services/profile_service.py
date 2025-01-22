from typing import Dict, Any, Optional, Tuple
from datetime import date

from app.db.crud import CRUDProfile
from app.core.calculations import calculate_calorie_goal, calculate_water_norm
from app.integrations.weather_api import WeatherAPI
from app.schemas.profile import UserProfile, ProfileCreate, ProfileUpdate
from app.utils.exceptions import ProfileError
from app.db.database import get_session


class ProfileService:
    def __init__(self):
        self.weather_api = WeatherAPI()

    async def _get_crud(self) -> CRUDProfile:
        session = await get_session()
        return CRUDProfile(session)

    async def create_or_update_profile(
        self,
        user_data: Dict[str, Any]
    ) -> bool:
        try:
            crud = await self._get_crud()

            temperature = await self.weather_api.get_temperature(user_data['city'])  # noqa: E501

            calorie_goal = calculate_calorie_goal(
                weight=user_data['weight'],
                height=user_data['height'],
                age=user_data['age'],
                activity_level=user_data['activity_level']
            )

            water_goal = calculate_water_norm(
                weight=user_data['weight'],
                activity_level=user_data['activity_level'],
                temperature=temperature
            )

            # Добавляем рассчитанные значения в данные
            profile_data = {
                **user_data,
                'calorie_goal': calorie_goal,
                'water_goal': water_goal,
            }

            # Проверяем существование пользователя
            user = await crud.get_user(user_data['user_id'])

            if user:
                profile_update = ProfileUpdate(**profile_data)
                await crud.update_user(user_data['user_id'], profile_update)
            else:
                profile_create = ProfileCreate(**profile_data)
                await crud.create_user(profile_create, user_data['user_id'])

            return True

        except Exception as e:
            raise ProfileError(f"Error creating/updating profile: {str(e)}")

    async def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """Получение профиля пользователя"""
        try:
            crud = await self._get_crud()
            user = await crud.get_user(user_id)

            if not user:
                return None

            temperature = await self.weather_api.get_temperature(user.city)
            water_goal = calculate_water_norm(
                weight=user.weight,
                activity_level=user.activity_level,
                temperature=temperature
            )

            return UserProfile(
                user_id=user.user_id,
                weight=user.weight,
                height=user.height,
                age=user.age,
                activity_level=user.activity_level,
                city=user.city,
                calorie_goal=user.calorie_goal,
                water_goal=water_goal,
                last_updated=user.updated_at
            )

        except Exception as e:
            raise ProfileError(f"Error getting profile: {str(e)}")

    async def get_daily_progress(
        self,
        user_id: int,
        target_date: date = None
    ) -> Tuple[float, float, float]:
        """Получение прогресса за день"""
        try:
            crud = await self._get_crud()

            if target_date is None:
                target_date = date.today()

            logs = await crud.get_daily_logs(user_id, target_date)

            water_consumed = sum(log.amount for log in logs['water_logs'])
            calories_consumed = sum(log.calories for log in logs['food_logs'])
            calories_burned = sum(log.calories_burned for log in logs['workout_logs'])  # noqa: E501

            return water_consumed, calories_consumed, calories_burned

        except Exception as e:
            raise ProfileError(f"Error getting daily progress: {str(e)}")
