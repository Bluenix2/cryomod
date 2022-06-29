from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, Router


class GuildCasesEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        guild_id = request.path_params['guild_id']

        if 'limit' not in request.query_params:
            raise HTTPException(400, "missing required query parameter 'limit'")

        try:
            limit = int(request.query_params['limit'])
            if 0 > limit > 100:
                raise HTTPException(400, "'limit' has to be between 1 and 100")
        except ValueError:
            raise HTTPException(400, "'limit' has to be an integer")

        conditions = ['guild_id = $1']

        if 'before' in request.query_params:
            try:
                before = int(request.query_params['before'])
            except ValueError:
                raise HTTPException(400, "'before' has to be an integer")

            conditions.append(f'case_id > {before}')

        if 'after' in request.query_params:
            try:
                after = int(request.query_params['after'])
            except ValueError:
                raise HTTPException(400, "'after' has to be an integer")

            conditions.append(f'case_id < {after}')

        cases = await request.app.state.db.fetch(
            f"""
            SELECT * FROM CASES
            WHERE {' AND '.join(conditions)}
            ORDER BY case_id ASC LIMIT $2;
            """,
            guild_id, limit
        )
        return JSONResponse([dict(case.items()) for case in cases])

    async def post(self, request: Request) -> Response:
        guild_id = request.path_params['guild_id']

        body = await request.json()
        if not body:
            raise HTTPException(400, 'body cannot be an empty object')

        if not isinstance(body, dict):
            raise HTTPException(400, 'body can only be an object')

        required_fields = ('type', 'actor_id', 'user_id')
        missing = "', '".join([field for field in required_fields if field not in body])
        if missing:
            raise HTTPException(400, f"missing required field(s) '{missing}'")

        case = await request.state.db.fetchrow(
            """
            with next_case_id AS (
                -- By constructing the query like this, we can take advantage
                -- of indexes, compared to using MAX()
                SELECT case_id + 1 FROM cases
                WHERE guild_id = $1
                ORDER BY case_id DESC LIMIT 1
            );

            INSERT INTO cases (
                guild_id, case_id, type, actor_id, user_id, notified, expires_at
            ) VALUES (
                $1, next_case_id, $2, $3, $4, $5, $6
            )
            RETURNING *;
            """,
            guild_id, body['type'], body['actor_id'], body['user_id'],
            body.get('notified', False), body.get('expires_at')
        )
        return JSONResponse(case)


class CaseEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        guild_id = request.path_params['guild_id']
        case_id = request.path_params['case_id']

        case = await request.app.state.db.fetchrow(
            'SELECT * FROM cases WHERE id = $1 AND guild_id = $1;',
            case_id, guild_id
        )
        return JSONResponse(dict(case.items()))

    async def patch(self, request: Request) -> Response:
        guild_id = request.path_params['guild_id']
        case_id = request.path_params['case_id']

        body = await request.json()
        if not body:
            # One might argue that we should simply ignore this, but it could
            # be hinting for an issue in the client layer.
            raise HTTPException(400, 'body cannot be an empty object')

        if not isinstance(body, dict):
            raise HTTPException(400, 'body can only be an object')

        notified = body.pop('notified', None)
        expires_at = body.pop('expires_at', None)

        if body:
            raise HTTPException(400, f"unknown key '{next(iter(body.keys()))}'")

        if notified is None and expires_at is None:
            raise HTTPException(400, "missing required field 'notified' or 'expires_at'")

        updated = await request.app.state.db.fetchrow(
            """"
            UPDATE cases
                SET notified = COALESCE($3, notified), expires_at = COALESCE($4, expires_at)
            WHERE id = $1 AND guild_id = $2 RETURNING *;
            """,
            case_id, guild_id, notified, expires_at
        )
        return JSONResponse(dict(updated.items()))


cases = Router(
    routes=[
        Route('/', GuildCasesEndpoint),
        Route('/{case_id:int}', CaseEndpoint),
    ]
)
