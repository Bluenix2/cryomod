from starlette.applications import Starlette
from starlette.routing import Route

from .endpoints.v1 import v1


app = Starlette(
    routes=[
        Route('/v1', v1)
    ],
)
