import re
from typing import Any

from .conftest import app

# Альтернативная реализация с возможностью передачи позиционных аргументов и повторением сигнатуры reverse() Django.
# Много кода и неудобная сигнатура, поэтому решил использовать более простой и удобный вариант из utils.py.


class PathNotFound(Exception):
    def __init__(self, name: str, path_params: list[Any] | dict[str, Any] | None) -> None:
        if isinstance(path_params, dict):
            params = ', '.join(list(key + '=' + str(value) for key, value in path_params.items()))
        elif isinstance(path_params, list):
            params = ', '.join(map(str, path_params))
        else:
            super().__init__('Path parameters are required.')
        super().__init__(f'No route exists for name "{name}" and params {params}.')


def reverse(viewname: str, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None):
    if args and kwargs:
        raise Exception('reverse() can`t accept both `args` and `kwargs` ')
    if not (args or kwargs):
        raise Exception('reverse() must accept one of parameters `args` or `kwargs`')
    for route in app.routes:
        if route.name == viewname:
            try:
                if args:
                    path = re.sub(r'\{([^}]+)\}', '{}', route.path)
                    return path.format(*args)
                elif kwargs:
                    return route.path.format(**kwargs)
            except Exception:
                pass
    raise PathNotFound(viewname, args or kwargs)
