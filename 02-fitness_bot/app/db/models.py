from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import (
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    Date,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base


class BaseMixin:
    """Базовый класс для всех моделей"""
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование модели в словарь"""
        return {
            column.name: getattr(self, column.name)
            for column in self.table.columns
        }


class User(BaseMixin, Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    activity_level: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    calorie_goal: Mapped[int] = mapped_column(Integer, nullable=True)
    water_goal: Mapped[int] = mapped_column(Integer, nullable=True)

    # Отношения
    water_logs: Mapped[List["WaterLog"]] = relationship(
        "WaterLog", back_populates="user", cascade="all, delete-orphan"
    )
    food_logs: Mapped[List["FoodLog"]] = relationship(
        "FoodLog", back_populates="user", cascade="all, delete-orphan"
    )
    workout_logs: Mapped[List["WorkoutLog"]] = relationship(
        "WorkoutLog", back_populates="user", cascade="all, delete-orphan"
    )
    daily_progress: Mapped[List["DailyProgress"]] = relationship(
        "DailyProgress", back_populates="user", cascade="all, delete-orphan"
    )


class WaterLog(BaseMixin, Base):
    """Модель логирования потребления воды"""
    __tablename__ = "water_logs"

    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="water_logs")


class FoodLog(BaseMixin, Base):
    """Модель логирования приема пищи"""
    __tablename__ = "food_logs"

    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)
    food_name: Mapped[str] = mapped_column(String(200), nullable=False)
    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    protein: Mapped[float] = mapped_column(Float, nullable=True)
    fats: Mapped[float] = mapped_column(Float, nullable=True)
    carbs: Mapped[float] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship(back_populates="food_logs")


class WorkoutLog(BaseMixin, Base):
    __tablename__ = "workout_logs"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    workout_type: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    intensity: Mapped[str] = mapped_column(String(50), nullable=False)
    calories_burned: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="workout_logs")


class DailyProgress(BaseMixin, Base):
    """Модель ежедневного прогресса"""
    __tablename__ = "daily_progress"

    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    water_consumed: Mapped[int] = mapped_column(Integer, default=0)
    calories_consumed: Mapped[int] = mapped_column(Integer, default=0)
    calories_burned: Mapped[int] = mapped_column(Integer, default=0)
    steps: Mapped[int] = mapped_column(Integer, default=0)
    weight_measurement: Mapped[float] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship(back_populates="daily_progress")

    table_args = (
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )
