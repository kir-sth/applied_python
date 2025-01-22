from pydantic import BaseModel, Field


class DailyProgressResponse(BaseModel):
    water_consumed: int = Field(0, description="Количество потребленной воды (мл)")  # noqa: E501
    water_target: int = Field(0, description="Целевое количество воды (мл)")
    calories_consumed: int = Field(0, description="Потребленные калории")
    calories_target: int = Field(0, description="Целевые калории")
    calories_burned: int = Field(0, description="Сожженные калории")
    calories_remaining: int = Field(0, description="Оставшиеся калории")
    workout_count: int = Field(0, description="Количество тренировок")
