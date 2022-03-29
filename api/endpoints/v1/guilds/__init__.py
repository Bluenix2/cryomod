from starlette.routing import Route, Router

from .cases import cases

guilds = Router(
    routes=[
        Route('/cases', cases)
    ]
)
