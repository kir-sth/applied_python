from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class FoodNutrients(BaseModel):
    """Схема для пищевой ценности продукта"""
    calories: float = Field(..., ge=0, description="Калории на 100г продукта")
    proteins: float = Field(0.0, ge=0, description="Белки на 100г продукта")
    fats: float = Field(0.0, ge=0, description="Жиры на 100г продукта")
    carbs: float = Field(0.0, ge=0, description="Углеводы на 100г продукта")

    model_config = {
        "json_schema_extra": {
            "example": {
                "calories": 52.0,
                "proteins": 0.3,
                "fats": 0.2,
                "carbs": 13.8
            }
        }
    }


class FoodItem(BaseModel):
    """Схема для продукта питания"""
    name: str = Field(..., min_length=1, max_length=100)
    calories: float = Field(..., ge=0)
    serving_size: float = Field(
        100.0, ge=0, description="Размер порции в граммах")
    proteins: Optional[float] = Field(0.0, ge=0)
    fats: Optional[float] = Field(0.0, ge=0)
    carbs: Optional[float] = Field(0.0, ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Яблоко",
                "calories": 52.0,
                "serving_size": 100.0,
                "proteins": 0.3,
                "fats": 0.2,
                "carbs": 13.8
            }
        }
    }


class FoodLogCreate(BaseModel):
    """Схема для создания записи о приеме пищи"""
    user_id: int
    food_name: str = Field(..., min_length=1, max_length=100)
    portion: float = Field(..., ge=1, le=2000)
    calories: float = Field(..., ge=0)


class FoodLog(FoodLogCreate):
    """Схема для записи о приеме пищи"""
    id: int
    timestamp: datetime
    nutrients: Optional[FoodNutrients] = None

    model_config = {
        "from_attributes": True
    }


class FoodDailySummary(BaseModel):
    """Схема для дневной сводки по питанию"""
    date: datetime
    total_calories: float = Field(0.0, ge=0)
    total_proteins: float = Field(0.0, ge=0)
    total_fats: float = Field(0.0, ge=0)
    total_carbs: float = Field(0.0, ge=0)
    meals_count: int = Field(0, ge=0)
    foods: List[FoodLog] = []


class FoodSearchResponse(BaseModel):
    """Схема для ответа на поиск продуктов"""
    query: str
    items: List[FoodItem]
    total_count: int = Field(0, ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "яблоко",
                "items": [
                    {
                        "name": "Яблоко",
                        "calories": 52.0,
                        "serving_size": 100.0,
                        "proteins": 0.3,
                        "fats": 0.2,
                        "carbs": 13.8
                    }
                ],
                "total_count": 1
            }
        }
    }


class UserNutritionGoals(BaseModel):
    """Схема для целей по питанию пользователя"""
    daily_calories: float = Field(..., ge=0)
    daily_proteins: Optional[float] = Field(None, ge=0)
    daily_fats: Optional[float] = Field(None, ge=0)
    daily_carbs: Optional[float] = Field(None, ge=0)


class NutritionProgress(BaseModel):
    """Схема для прогресса по питанию"""
    consumed_calories: float = Field(0.0, ge=0)
    target_calories: float = Field(..., ge=0)
    consumed_proteins: Optional[float] = Field(0.0, ge=0)
    target_proteins: Optional[float] = Field(None, ge=0)
    consumed_fats: Optional[float] = Field(0.0, ge=0)
    target_fats: Optional[float] = Field(None, ge=0)
    consumed_carbs: Optional[float] = Field(0.0, ge=0)
    target_carbs: Optional[float] = Field(None, ge=0)
    remaining_calories: float = Field(0.0)
    completion_percentage: float = Field(0.0, ge=0, le=100)
