from starlette.applications import Starlette
from starlette.routing import Route

from . import utils
from .database import db_lifespan
from .endpoints.v1 import v1

app = Starlette(
    routes=[
        Route('/v1', v1)
    ],
    lifespan=db_lifespan,
)
