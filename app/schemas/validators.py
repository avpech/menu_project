from typing import TypeVar

ValueType = TypeVar('ValueType')


def convert_price_to_float(value: str) -> float:
    """
    Конвертация поля из `str` во `float`.
    Проверка на неотрицательное значение.
    """
    price = float(value)
    if price < 0:
        raise ValueError('price не может иметь отрицательное значение')
    return price


def field_cannot_be_null(value: ValueType) -> ValueType:
    """Валидация на недопустимость передачи полю значения null."""
    if value is None:
        raise ValueError('Значение поля не может быть null.')
    return value
