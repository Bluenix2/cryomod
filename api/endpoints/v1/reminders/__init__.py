from starlette.routing import Route, Router

from .paginated import RemindersEndpoint
from .specific import SpecificReminderEndpoint


reminders = Router(
    routes=[
        Route('/', RemindersEndpoint),
        Route('/{remind_id:int}', SpecificReminderEndpoint),
    ]
)
