from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RemindersEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        guild_id = request.query_params.get('guild_id')
        author_id = request.query_params.get('author_id')

        if 'limit' not in request.query_params:
            raise HTTPException(400, detail="missing required query parameter 'limit'")

        try:
            limit = int(request.query_params['limit'])
            if 0 > limit > 100:
                raise HTTPException(400, detail="'limit' has to be between 1 and 100")
        except ValueError:
            raise HTTPException(400, detail="'limit' has to be an integer")

        conditions = []

        if 'guild_id' not in request.query_params and 'author_id' not in request.query_params:
            raise HTTPException(400, detail="one of 'guild_id' and 'author_id' is required")

        if 'guild_id' in request.query_params:
            try:
                guild_id = int(request.query_params['guild_id'])
            except ValueError:
                raise HTTPException(400, detail="'guild_id' has to be an integer")

            conditions.append(f'guild_id = {guild_id}')

        if 'author_id' in request.query_params:
            try:
                author_id = int(request.query_params['author_id'])
            except ValueError:
                raise HTTPException(400, detail="'author_id' has to be an integer")

            conditions.append(f'author_id = {author_id}')

        if 'before' in request.query_params:
            try:
                before = int(request.query_params['before'])
            except ValueError:
                raise HTTPException(400, detail="'before' has to be an integer")

            conditions.append(f'id > {before}')
        else:
            before = None  # We need to keep this around for the 'after' check

        if 'after' in request.query_params:
            try:
                after = int(request.query_params['after'])
            except ValueError:
                raise HTTPException(400, detail="'after' has to be an integer")

            if before is not None and before >= after:
                raise HTTPException(400, detail="'after' has to be larger than 'before'")

            conditions.append(f'id < {after}')

        reminders = await request.app.state.db.fetch(
            f"""
            SELECT * FROM reminders WHERE {' AND '.join(conditions)}
            ORDER BY id ASC LIMIT $1;
            """,
            limit
        )

        return JSONResponse(reminders)

    async def post(self, request: Request) -> Response:
        body = await request.json()
        if not body:
            raise HTTPException(400, detail='body cannot be an empty object')

        if not isinstance(body, dict):
            raise HTTPException(400, detail='body can only be an object')

        required_fields = ('channel_id', 'author_id', 'expires_at')
        missing = "', '".join([field for field in required_fields if field not in body])
        if missing:
            raise HTTPException(400, detail=f"missing required field(s) '{missing}'")

        reminder = await request.app.state.db.fetchrow(
            """
            INSERT INTO reminders (channel_id, author_id, guild_id, expires_at)
            VALUES ($1, $2, $3, $4) RETURNING *;
            """,
            body['channel_id'], body['author_id'], body.get('guild_id'), body['expires_at']
        )
        return JSONResponse(reminder)
