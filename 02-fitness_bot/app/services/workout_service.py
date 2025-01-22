from datetime import datetime, time
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import WorkoutLog, User, FoodLog
from app.schemas.workout import WorkoutCreate, DailyProgress
from app.utils.exceptions import ValidationError


class WorkoutService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def calculate_calories_burned(
        self,
        workout_type: str,
        duration: int,
        intensity: str
    ) -> int:
        """Расчет сожженных калорий"""
        calories_per_minute = {
            "Бег": {"low": 8, "medium": 10, "high": 12},
            "Ходьба": {"low": 3, "medium": 4, "high": 5},
            "Велосипед": {"low": 5, "medium": 7, "high": 9},
            "Плавание": {"low": 6, "medium": 8, "high": 10},
            "Силовая тренировка": {"low": 4, "medium": 6, "high": 8},
            "Йога": {"low": 2, "medium": 3, "high": 4},
            "Другое": {"low": 4, "medium": 5, "high": 6}
        }
        return int(calories_per_minute[workout_type][intensity] * duration)

    async def log_workout(self, workout_data: WorkoutCreate) -> WorkoutLog:
        """Логирование тренировки"""
        try:
            user = await self.session.execute(
                select(User).where(User.user_id == workout_data.user_id)
            )
            user = user.scalar_one_or_none()

            if not user:
                raise ValidationError("Пользователь не найден")

            workout_log = WorkoutLog(
                user_id=workout_data.user_id,
                workout_type=workout_data.workout_type,
                duration=workout_data.duration,
                intensity=workout_data.intensity,
                calories_burned=workout_data.calories_burned,
                timestamp=datetime.utcnow()
            )

            self.session.add(workout_log)
            await self.session.commit()
            return workout_log

        except Exception as e:
            await self.session.rollback()
            raise ValidationError(f"Ошибка при сохранении тренировки: {str(e)}")  # noqa E501

    async def get_daily_stats(self, user_id: int) -> DailyProgress:
        """Получение статистики за день"""
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, time.min)
            today_end = datetime.combine(today, time.max)

            # Получаем сумму сожженных калорий за день
            burned_result = await self.session.execute(
                select(func.sum(WorkoutLog.calories_burned)).where(
                    and_(
                        WorkoutLog.user_id == user_id,
                        WorkoutLog.timestamp >= today_start,
                        WorkoutLog.timestamp <= today_end
                    )
                )
            )
            total_burned = burned_result.scalar() or 0

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

            # Получаем сумму потребленных калорий за день
            consumed_result = await self.session.execute(
                select(func.sum(FoodLog.calories)).where(
                    and_(
                        FoodLog.user_id == user_id,
                        FoodLog.timestamp >= today_start,
                        FoodLog.timestamp <= today_end
                    )
                )
            )
            calories_consumed = consumed_result.scalar() or 0

            # Получаем цель по калориям пользователя
            user_result = await self.session.execute(
                select(User.calorie_goal).where(User.user_id == user_id)
            )
            calorie_goal = user_result.scalar() or 2000

            # Расчет оставшихся калорий
            calories_remaining = calorie_goal - calories_consumed + total_burned  # noqa E501

            return DailyProgress(
                date=today_start,
                total_burned=total_burned,
                calories_consumed=calories_consumed,
                calories_remaining=calories_remaining,
                workout_count=workout_count
            )

        except Exception as e:
            raise ValidationError(f"Ошибка при получении статистики: {str(e)}")
