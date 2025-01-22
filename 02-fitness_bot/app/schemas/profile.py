from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import IntEnum


class ActivityLevel(IntEnum):
    """Уровни физической активности"""
    SEDENTARY = 1  # Сидячий образ жизни
    MODERATE = 2   # Умеренная активность
    ACTIVE = 3     # Высокая активность
    VERY_ACTIVE = 4  # Очень высокая активность


class ProfileCreate(BaseModel):
    """Схема для создания профиля"""
    weight: float = Field(..., gt=30, lt=300, description="Вес в килограммах")
    height: float = Field(..., gt=100, lt=250, description="Рост в сантиметрах")  # noqa: E501
    age: int = Field(..., gt=14, lt=100, description="Возраст в годах")
    activity_level: ActivityLevel = Field(..., description="Уровень физической активности")  # noqa: E501
    city: str = Field(..., min_length=2, max_length=100, description="Город проживания")  # noqa: E501
    calorie_goal: Optional[int] = None
    water_goal: Optional[int] = None

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "weight": 70.5,
                "height": 175,
                "age": 30,
                "activity_level": 2,
                "city": "Москва",
                "calorie_goal": None,
                "water_goal": None
            }
        }


class ProfileUpdate(BaseModel):
    """Схема для обновления профиля"""
    weight: Optional[float] = Field(None, gt=30, lt=300)
    height: Optional[float] = Field(None, gt=100, lt=250)
    age: Optional[int] = Field(None, gt=14, lt=100)
    activity_level: Optional[ActivityLevel] = None
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    calorie_goal: Optional[int] = None
    water_goal: Optional[int] = None

    class Config:
        use_enum_values = True


class UserProfile(BaseModel):
    """Полная модель профиля пользователя"""
    user_id: int
    weight: float
    height: float
    age: int
    activity_level: ActivityLevel
    city: str
    calorie_goal: int
    water_goal: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class DailyProgress(BaseModel):
    """Модель дневного прогресса"""
    water_consumed: float = Field(default=0, ge=0)
    calories_consumed: float = Field(default=0, ge=0)
    calories_burned: float = Field(default=0, ge=0)
    water_goal: float
    calorie_goal: float
    date: datetime

    @property
    def water_progress(self) -> float:
        """Процент выполнения цели по воде"""
        return (self.water_consumed / self.water_goal) * 100 if self.water_goal else 0  # noqa E501

    @property
    def calorie_progress(self) -> float:
        """Процент выполнения цели по калориям"""
        return (self.calories_consumed / self.calorie_goal) * 100 if self.calorie_goal else 0  # noqa E501

    @property
    def remaining_calories(self) -> float:
        """Оставшиеся калории"""
        return max(0, self.calorie_goal - (self.calories_consumed - self.calories_burned))  # noqa E501


class WeeklyStats(BaseModel):
    """Модель недельной статистики"""
    start_date: datetime
    end_date: datetime
    daily_stats: list[DailyProgress]

    @property
    def average_water_consumed(self) -> float:
        """Среднее потребление воды за неделю"""
        if not self.daily_stats:
            return 0
        return sum(day.water_consumed for day in self.daily_stats) / len(self.daily_stats)  # noqa E501

    @property
    def average_calories_consumed(self) -> float:
        """Среднее потребление калорий за неделю"""
        if not self.daily_stats:
            return 0
        return sum(day.calories_consumed for day in self.daily_stats) / len(self.daily_stats)  # noqa E501

    @property
    def average_calories_burned(self) -> float:
        """Среднее количество сожженных калорий за неделю"""
        if not self.daily_stats:
            return 0
        return sum(day.calories_burned for day in self.daily_stats) / len(self.daily_stats)  # noqa E501


class ProfileResponse(BaseModel):
    """Модель ответа с данными профиля"""
    profile: UserProfile
    daily_progress: Optional[DailyProgress] = None
    weekly_stats: Optional[WeeklyStats] = None
    message: Optional[str] = None
    status: str = "success"


class ProfileError(BaseModel):
    """Модель ошибки профиля"""
    message: str
    status: str = "error"
    error_code: Optional[str] = None
    details: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Не удалось обновить профиль",
                "status": "error",
                "error_code": "PROFILE_UPDATE_ERROR",
                "details": {"field": "weight", "reason": "Value out of range"}
            }
        }
