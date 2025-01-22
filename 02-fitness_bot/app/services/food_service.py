from datetime import datetime, time
from typing import Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, FoodLog
from app.utils.exceptions import ValidationError
from app.integrations.food_api import FoodAPI


class FoodService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.food_api = FoodAPI()

    async def log_food(
        self,
        user_id: int,
        food_name: str,
        portion: float,
        calories: float,
        protein: float = None,
        fats: float = None,
        carbs: float = None
    ) -> None:
        """Логирование приема пищи"""
        # Проверяем существование пользователя
        user = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise ValidationError("Пользователь не найден")

        try:
            food_log = FoodLog(
                user_id=user_id,
                food_name=food_name,
                calories=int(calories),
                protein=protein,
                fats=fats,
                carbs=carbs,
                timestamp=datetime.utcnow()
            )
            self.session.add(food_log)
            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            raise ValidationError(
                f"Не удалось сохранить информацию о приеме пищи: {str(e)}")

    async def get_daily_progress(self, user_id: int) -> Tuple[float, float]:
        """
        Получает прогресс потребления калорий за текущий день
        Возвращает (потребленные калории, целевые калории)
        """
        try:
            # Получаем профиль пользователя для целевых калорий
            user = await self.session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user.scalar_one_or_none()

            if not user:
                raise ValidationError("Пользователь не найден")

            # Получаем сумму калорий за текущий день
            today = datetime.now().date()
            today_start = datetime.combine(today, time.min)
            today_end = datetime.combine(today, time.max)

            result = await self.session.execute(
                select(func.sum(FoodLog.calories)).where(
                    and_(
                        FoodLog.user_id == user_id,
                        FoodLog.timestamp >= today_start,
                        FoodLog.timestamp <= today_end
                    )
                )
            )

            consumed_calories = result.scalar() or 0
            return float(consumed_calories), float(user.calorie_goal or 2000)

        except Exception as e:
            raise ValidationError(f"Ошибка при получении прогресса: {str(e)}")

    async def search_food(self, query: str) -> list:
        """Поиск продукта через API"""
        try:
            food_items = await self.food_api.search_food(query)
            if not food_items:
                return []
            return food_items
        except Exception as e:
            raise ValidationError(f"Ошибка при поиске продукта: {str(e)}")
