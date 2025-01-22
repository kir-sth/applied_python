from datetime import datetime, time
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, WaterLog, FoodLog, WorkoutLog
from app.schemas.progress import DailyProgressResponse


class ProgressService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_daily_progress(self, user_id: int) -> DailyProgressResponse:
        """Получение прогресса за текущий день"""
        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        # Получаем данные пользователя
        user = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user.scalar_one_or_none()
        if not user:
            raise ValueError("Пользователь не найден")

        # Получаем потребление воды
        water_result = await self.session.execute(
            select(func.sum(WaterLog.amount)).where(
                and_(
                    WaterLog.user_id == user_id,
                    WaterLog.timestamp >= today_start,
                    WaterLog.timestamp <= today_end
                )
            )
        )
        water_consumed = water_result.scalar() or 0

        # Получаем потребленные калории
        calories_result = await self.session.execute(
            select(func.sum(FoodLog.calories)).where(
                and_(
                    FoodLog.user_id == user_id,
                    FoodLog.timestamp >= today_start,
                    FoodLog.timestamp <= today_end
                )
            )
        )
        calories_consumed = calories_result.scalar() or 0

        # Получаем сожженные калории
        burned_result = await self.session.execute(
            select(func.sum(WorkoutLog.calories_burned)).where(
                and_(
                    WorkoutLog.user_id == user_id,
                    WorkoutLog.timestamp >= today_start,
                    WorkoutLog.timestamp <= today_end
                )
            )
        )
        calories_burned = burned_result.scalar() or 0

        # Получаем количество тренировок
        workout_count_result = await self.session.execute(
            select(func.count(WorkoutLog.id)).where(
                and_(
                    WorkoutLog.user_id == user_id,
                    WorkoutLog.timestamp >= today_start,
                    WorkoutLog.timestamp <= today_end
                )
            )
        )
        workout_count = workout_count_result.scalar() or 0

        # Рассчитываем оставшиеся калории
        calories_remaining = user.calorie_goal - calories_consumed + calories_burned  # noqa: E501

        return DailyProgressResponse(
            water_consumed=water_consumed,
            water_target=user.water_goal,
            calories_consumed=calories_consumed,
            calories_target=user.calorie_goal,
            calories_burned=calories_burned,
            calories_remaining=calories_remaining,
            workout_count=workout_count
        )
