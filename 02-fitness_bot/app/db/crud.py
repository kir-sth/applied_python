from app.utils.exceptions import ProfileError
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.db.models import User, WaterLog, FoodLog, WorkoutLog, DailyProgress
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, date
from typing import Optional, List, Dict, Any


class CRUDProfile:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID
        """
        query = select(User).where(User.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        profile_data: ProfileCreate,
        user_id: int
    ) -> User:
        """
        Создание нового пользователя
        """
        try:
            db_user = User(
                user_id=user_id,
                weight=profile_data.weight,
                height=profile_data.height,
                age=profile_data.age,
                activity_level=profile_data.activity_level,
                city=profile_data.city,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user
        except Exception as e:
            await self.session.rollback()
            raise ProfileError(str(e))

    async def update_user(
        self,
        user_id: int,
        profile_data: ProfileUpdate
    ) -> User:
        """
        Обновление данных пользователя
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                raise ProfileError(user_id)

            update_data = profile_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise ProfileError(str(e))

    async def delete_user(self, user_id: int) -> bool:
        """
        Удаление пользователя
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            await self.session.delete(user)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise ProfileError(f"Error deleting user: {str(e)}")

    async def log_water(
        self,
        user_id: int,
        amount: int,
        timestamp: Optional[datetime] = None
    ) -> WaterLog:
        """
        Логирование потребления воды
        """
        try:
            water_log = WaterLog(
                user_id=user_id,
                amount=amount,
                timestamp=timestamp or datetime.utcnow()
            )
            self.session.add(water_log)
            await self.session.commit()
            await self.session.refresh(water_log)
            return water_log
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error logging water: {str(e)}")

    async def log_food(
        self,
        user_id: int,
        food_name: str,
        calories: int,
        timestamp: Optional[datetime] = None
    ) -> FoodLog:
        """
        Логирование приема пищи
        """
        try:
            food_log = FoodLog(
                user_id=user_id,
                food_name=food_name,
                calories=calories,


                timestamp=timestamp or datetime.utcnow()
            )
            self.session.add(food_log)
            await self.session.commit()
            await self.session.refresh(food_log)
            return food_log
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error logging food: {str(e)}")

    async def log_workout(
        self,
        user_id: int,
        workout_type: str,
        duration: int,
        calories_burned: int,
        timestamp: Optional[datetime] = None
    ) -> WorkoutLog:
        """
        Логирование тренировки
        """
        try:
            workout_log = WorkoutLog(
                user_id=user_id,
                workout_type=workout_type,
                duration=duration,
                calories_burned=calories_burned,
                timestamp=timestamp or datetime.utcnow()
            )
            self.session.add(workout_log)
            await self.session.commit()
            await self.session.refresh(workout_log)
            return workout_log
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error logging workout: {str(e)}")

    async def get_daily_logs(
        self,
        user_id: int,
        target_date: date
    ) -> Dict[str, List[Any]]:
        """
        Получение всех логов за день
        """
        try:
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())

            # Получаем логи воды
            water_query = select(WaterLog).where(
                and_(
                    WaterLog.user_id == user_id,
                    WaterLog.timestamp.between(start_datetime, end_datetime)
                )
            )
            water_result = await self.session.execute(water_query)
            water_logs = water_result.scalars().all()

            # Получаем логи еды
            food_query = select(FoodLog).where(
                and_(
                    FoodLog.user_id == user_id,
                    FoodLog.timestamp.between(start_datetime, end_datetime)
                )
            )
            food_result = await self.session.execute(food_query)
            food_logs = food_result.scalars().all()

            # Получаем логи тренировок
            workout_query = select(WorkoutLog).where(
                and_(
                    WorkoutLog.user_id == user_id,
                    WorkoutLog.timestamp.between(start_datetime, end_datetime)
                )
            )
            workout_result = await self.session.execute(workout_query)
            workout_logs = workout_result.scalars().all()

            return {
                "water_logs": water_logs,
                "food_logs": food_logs,
                "workout_logs": workout_logs
            }
        except Exception as e:
            raise Exception(f"Error getting daily logs: {str(e)}")

    async def get_weekly_logs(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Получение логов за неделю
        """
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            # Получаем все логи за период
            daily_progress_query = select(DailyProgress).where(
                and_(
                    DailyProgress.user_id == user_id,
                    DailyProgress.date.between(start_datetime, end_datetime)
                )
            )
            result = await self.session.execute(daily_progress_query)
            progress_logs = result.scalars().all()

            return [log.to_dict() for log in progress_logs]
        except Exception as e:
            raise Exception(f"Error getting weekly logs: {str(e)}")

    async def update_daily_progress(
        self,
        user_id: int,
        target_date: date,
        water_consumed: int,
        calories_consumed: int,
        calories_burned: int
    ) -> DailyProgress:
        """
        Обновление дневного прогресса
        """
        try:
            progress = await self.get_daily_progress(user_id, target_date)
            if not progress:
                progress = DailyProgress(
                    user_id=user_id,
                    date=target_date,
                    water_consumed=water_consumed,
                    calories_consumed=calories_consumed,
                    calories_burned=calories_burned
                )
                self.session.add(progress)
            else:
                progress.water_consumed = water_consumed
                progress.calories_consumed = calories_consumed
                progress.calories_burned = calories_burned

            await self.session.commit()
            await self.session.refresh(progress)
            return progress
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error updating daily progress: {str(e)}")


class CRUDWater:
    def __init__(self, session):
        self.session = session

    async def create_water_log(
        self,
        user_id: int,
        amount: float,
        timestamp: datetime
    ) -> WaterLog:
        water_log = WaterLog(
            user_id=user_id,
            amount=amount,
            timestamp=timestamp
        )
        self.session.add(water_log)
        await self.session.commit()
        return water_log

    async def get_daily_water_amount(
        self,
        user_id: int,
        target_date: date = None
    ) -> float:
        if target_date is None:
            target_date = date.today()

        query = select(func.sum(WaterLog.amount)).where(
            WaterLog.user_id == user_id,
            func.date(WaterLog.timestamp) == target_date
        )
        result = await self.session.execute(query)
        return result.scalar() or 0


class CRUDFood:
    def init(self, session):
        self.session = session

    async def create_food_log(
        self,
        user_id: int,
        food_name: str,
        portion: float,
        calories: float,
        timestamp: datetime
    ) -> FoodLog:
        food_log = FoodLog(
            user_id=user_id,
            food_name=food_name,
            portion=portion,
            calories=calories,
            timestamp=timestamp
        )
        self.session.add(food_log)
        await self.session.commit()
        return food_log

    async def get_daily_calories(
        self,
        user_id: int,
        target_date: date = None
    ) -> float:
        if target_date is None:
            target_date = date.today()

        query = select(func.sum(FoodLog.calories)).where(
            FoodLog.user_id == user_id,
            func.date(FoodLog.timestamp) == target_date
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_user_calorie_goal(self, user_id: int) -> float:
        query = select(User.calorie_goal).where(User.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() or 2000  # default value
