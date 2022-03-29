from starlette.routing import Route, Router

from .guilds import guilds

v1 = Router(
    routes=[
        Route('/guilds/{guild_id:snowflake}', guilds),
    ],
)
