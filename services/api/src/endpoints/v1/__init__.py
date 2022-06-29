from starlette.routing import Route, Router

from .guilds import guilds
from .reminders import reminders


v1 = Router(
    routes=[
        Route('/guilds/{guild_id:snowflake}', guilds),
        Route('/reminders', reminders)
    ],
)
