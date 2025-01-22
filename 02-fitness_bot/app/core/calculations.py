ACTIVITY_MULTIPLIERS = {
    1: 1.2,  # Сидячий образ жизни
    2: 1.375,  # Умеренная активность
    3: 1.55,  # Высокая активность
    4: 1.725  # Очень высокая активность
}


def calculate_calorie_goal(
    weight: float,
    height: float,
    age: int,
    activity_level: int,
    gender: str = 'M'
) -> int:
    """
    Расчет суточной нормы калорий по формуле Миффлина-Сан Жеора
    """
    # Базовый обмен веществ
    if gender == 'M':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # Умножаем на коэффициент активности
    daily_calories = bmr * ACTIVITY_MULTIPLIERS[activity_level]

    return round(daily_calories)


def calculate_water_norm(
    weight: float,
    activity_level: int,
    temperature: float
) -> int:
    """
    Расчет суточной нормы воды в мл
    """
    # Базовая норма воды
    base_water = weight * 30

    # Дополнительная вода в зависимости от активности
    activity_water = (activity_level - 1) * 250

    # Корректировка по температуре
    temp_adjustment = 500 if temperature > 25 else 0

    total_water = base_water + activity_water + temp_adjustment

    return round(total_water)
