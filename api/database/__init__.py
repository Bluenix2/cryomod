import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from anyio import Path
from starlette.applications import Starlette
from triopg import create_pool


_log = logging.getLogger(__name__)


async def _bootstrap_migrations(database) -> None:
    await database.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            name TEXT PRIMARY KEY,
            applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'UTC')
        );
    """)


async def migrate(database) -> None:
    """Run migrations under the migrations folder."""
    await _bootstrap_migrations(database)

    last = await database.fetchval('SELECT name FROM migrations ORDER BY name ASC;')
    if last is None:
        _log.info('Found no migrations to apply; skipping.')
        return

    folder = Path('./migrations')
    to_do = sorted(
        [
            path async for path in folder.iterdir()
            if await path.is_file() and path.name > last
        ],
        key=lambda path: path.name
    )
    _log.info(f"Applying {len(to_do)} migrations since '{last}'")

    # If any migration goes wrong, we should rollback the database completely
    async with database.transaction():
        for path in to_do:
            await database.execute(path.read_text())
            await database.execute('INSERT INTO migrations (name) VALUES ($1);', path.name)
            _log.debug(f"Applied migration '{path.name}'")


@asynccontextmanager
async def db_lifespan(app: Starlette) -> AsyncGenerator[None, Any]:
    """Lifespan creating and cleaning up Postgres connection pool."""
    async with create_pool() as app.state.db:
        await migrate(app.state.db)
        yield
