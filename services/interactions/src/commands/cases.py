from typing import Optional

from wumpy import interactions
from wumpy.interactions import CommandInteraction
from wumpy.models import User


@interactions.command()
async def cases(
    inter: CommandInteraction,
    *,
    user: 
    actor: Optional[User] = interactions.Option(description='The actor who applied the case'),
) -> None:
    ...
