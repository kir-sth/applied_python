from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkoutBase(BaseModel):
    """Базовая схема для тренировки"""
    workout_type: str = Field(
        ...,
        description="Тип тренировки",
        examples=["Бег", "Ходьба", "Велосипед",
                  "Плавание", "Силовая тренировка", "Йога", "Другое"]
    )
    duration: int = Field(
        ...,
        ge=1,
        le=300,
        description="Продолжительность в минутах"
    )
    intensity: str = Field(
        ...,
        description="Интенсивность тренировки",
        examples=["low", "medium", "high"]
    )


class WorkoutCreate(WorkoutBase):
    """Схема для создания записи о тренировке"""
    user_id: int = Field(..., description="ID пользователя")
    calories_burned: int = Field(
        ...,
        ge=0,
        description="Сожженные калории"
    )


class WorkoutResponse(WorkoutBase):
    """Схема для ответа с данными о тренировке"""
    id: int
    user_id: int
    timestamp: datetime
    calories_burned: int

    class Config:
        from_attributes = True


class WorkoutStats(BaseModel):
    """Схема для статистики тренировок"""
    total_duration: int = Field(
        0,
        description="Общая продолжительность тренировок"
    )
    total_burned: int = Field(
        0,
        description="Всего сожжено калорий"
    )
    calories_consumed: int = Field(
        0,
        description="Всего потреблено калорий"
    )
    workout_count: int = Field(
        0,
        description="Количество тренировок"
    )
    average_duration: Optional[float] = Field(
        None,
        description="Средняя продолжительность"
    )
    average_calories: Optional[float] = Field(
        None,
        description="Среднее количество сожженных калорий"
    )


class DailyProgress(BaseModel):
    """Схема для дневного прогресса"""
    date: datetime
    total_burned: int = Field(
        0,
        description="Всего сожжено калорий"
    )
    calories_consumed: int = Field(
        0,
        description="Всего потреблено калорий"
    )
    calories_remaining: int = Field(
        0,
        description="Осталось калорий"
    )
    workout_count: int = Field(
        0,
        description="Количество тренировок"
    )


class WorkoutFilter(BaseModel):
    """Схема для фильтрации тренировок"""
    start_date: Optional[datetime] = Field(
        None,
        description="Начальная дата"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Конечная дата"
    )
    workout_type: Optional[str] = Field(
        None,
        description="Тип тренировки"
    )
    intensity: Optional[str] = Field(
        None,
        description="Интенсивность"
    )
    min_duration: Optional[int] = Field(
        None,
        ge=1,
        le=300,
        description="Минимальная продолжительность"
    )
    max_duration: Optional[int] = Field(
        None,
        ge=1,
        le=300,
        description="Максимальная продолжительность"
    )


class WorkoutUpdate(BaseModel):
    """Схема для обновления записи о тренировке"""
    workout_type: Optional[str] = Field(
        None,
        description="Тип тренировки",
        examples=["Бег", "Ходьба", "Велосипед", "Плавание",
                  "Силовая тренировка", "Йога", "Другое"]
    )
    duration: Optional[int] = Field(
        None,
        ge=1,
        le=300,
        description="Продолжительность в минутах"
    )
    intensity: Optional[str] = Field(
        None,
        description="Интенсивность тренировки",
        examples=["low", "medium", "high"]
    )
    calories_burned: Optional[int] = Field(
        None,
        ge=0,
        description="Сожженные калории"
    )
