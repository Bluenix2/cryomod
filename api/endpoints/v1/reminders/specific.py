from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class SpecificReminderEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        remind_id = request.path_params['remind_id']

        reminder = await request.app.state.db.fetchrow(
            'SELECT * FROM reminders WHERE id = $1;', remind_id
        )
        if reminder is None:
            raise HTTPException(404, detail=f'unknown reminder with ID {remind_id}')

        return JSONResponse(reminder)

    async def delete(self, request: Request) -> Response:
        remind_id = request.path_params['remind_id']

        author_id = request.query_params.get('author_id')
        if author_id is not None:
            reminder = await request.app.state.db.fetchrow(
                'DELETE FROM reminders WHERE id = $1 AND author_id = $2 RETURNING *;',
                remind_id, author_id
            )
            if reminder is None:
                raise HTTPException(
                    404, detail=f'unknown reminder with ID {remind_id} from author {author_id}'
                )

            return JSONResponse(reminder)

        reminder = await request.app.state.db.fetchrow(
            'DELETE FROM reminders WHERE id = $1 RETURNING *;', remind_id
        )
        if reminder is None:
            raise HTTPException(404, detail=f'unknown reminder with ID {remind_id}')

        return JSONResponse(reminder)
