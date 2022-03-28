from starlette.routing import Router
from starlette.endpoints import HTTPEndpoint


cases = Router()


class GuildCases(HTTPEndpoint):
    async def get(self,)
