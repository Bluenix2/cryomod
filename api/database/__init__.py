from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from anyio import Path
from starlette.applications import Starlette
from triopg import create_pool


async def migrate(app: Starlette) -> None:
    """Run migrations under the migrations folder."""
    # If any migration goes wrong, we should rollback the database completely
    async with app.state.db.transaction():
        folder = Path('./migrations')
        async for path in folder.iterdir():
            if not await path.is_file():
                continue

            await app.state.db.execute(path.read_text())


@asynccontextmanager
async def db_lifespan(app: Starlette) -> AsyncGenerator[None, Any]:
    """Lifespan creating and cleaning up Postgres connection pool."""
    async with create_pool() as app.state.db:
        await migrate(app)
        yield
