from datetime import datetime

from app.db.crud import CRUDWater
from app.db.database import get_session
from app.schemas.water import WaterLog
from app.services.profile_service import ProfileService
from app.utils.exceptions import ValidationError


class WaterService:
    def __init__(self):
        self.profile_service = ProfileService()

    async def _get_crud(self) -> CRUDWater:
        session = await get_session()
        return CRUDWater(session)

    def validate_amount(self, amount: int) -> None:
        """Валидация количества воды"""
        if not isinstance(amount, (int, float)):
            raise ValidationError("Количество воды должно быть числом")
        if amount < 50 or amount > 3000:
            raise ValidationError(
                "Количество воды должно быть от 50 до 3000 мл")

    async def log_water(self, user_id: int, amount: int) -> WaterLog:
        """Логирование потребления воды"""
        try:
            self.validate_amount(amount)

            crud = await self._get_crud()
            water_log = await crud.create_water_log(
                user_id=user_id,
                amount=amount,
                timestamp=datetime.now()
            )

            return water_log
        except Exception as e:
            raise Exception(f"Error logging water: {str(e)}")

    async def get_daily_progress(self, user_id: int) -> tuple[float, float]:
        """Получение прогресса за день"""
        try:
            profile = await self.profile_service.get_profile(user_id)
            if not profile:
                raise Exception("Profile not found")

            crud = await self._get_crud()
            consumed = await crud.get_daily_water_amount(user_id)

            return consumed, profile.water_goal
        except Exception as e:
            raise Exception(f"Error getting water progress: {str(e)}")
