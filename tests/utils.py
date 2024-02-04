from .conftest import app


def reverse(viewname: str, **kwargs):
    return app.url_path_for(viewname, **kwargs)
