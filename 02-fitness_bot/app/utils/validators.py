def validate_weight(weight: float) -> bool:
    return 30 < weight < 300


def validate_height(height: float) -> bool:
    return 100 < height < 250


def validate_age(age: int) -> bool:
    return 14 < age < 100


def validate_activity_level(activity_level: int) -> bool:
    return 1 <= activity_level <= 4
