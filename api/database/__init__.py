from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from starlette.applications import Starlette
from triopg import create_pool


@asynccontextmanager
async def db_lifespan(app: Starlette) -> AsyncGenerator[None, Any]:
    """Lifespan creating and cleaning up Postgres connection pool."""
    async with create_pool() as app.state.db:
        yield
