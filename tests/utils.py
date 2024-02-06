from starlette.datastructures import URLPath

from .conftest import app


def reverse(viewname: str, **kwargs) -> URLPath:
    """
    Получение `url` по имени view-функции.

    Path-параметры передаются именованными аргументами.
    """
    return app.url_path_for(viewname, **kwargs)
