import re
from datetime import datetime, timezone, tzinfo, timedelta
from contextlib import suppress

from wumpy import interactions


_DURATION_REGEX = re.compile(
    r"((?P<years>\d+?) ?(years|year|Y|y) ?)?"
    r"((?P<months>\d+?) ?(months|month|m) ?)?"
    r"((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?"
    r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
    r"((?P<hours>\d+?) ?(hours|hour|H|h) ?)?"
    r"((?P<minutes>\d+?) ?(minutes|minute|M) ?)?"
    r"((?P<seconds>\d+?) ?(seconds|second|S|s))?"
)


def parse_datetime(value: str, tz: tzinfo = timezone.utc) -> datetime:
    """Parse a user-inputted string value to a datetime object.

    If the value can only be parsed to a naive datetime, it will be made aware
    with the timezone passed into it. POSIX timestamps and deltas are both
    interpreted as UTC.

    Parameters:
        value: The user-inputted string to parse.
        tz: Timezone to interpret naive datetimes in.

    Raises:
        ValueError: The value could not be parsed to a datetime.

    Returns:
        The parsed, aware, datetime. The datetime's timezone-info may differ
        from the value of the `tz` parameter.
    """
    if value.isdecimal():
        return datetime.fromtimestamp(float(value), tz=tz)

    match = _DURATION_REGEX.fullmatch(value)
    if match:
        delta = timedelta(**{u: int(v) for (u, v) in match.groupdict(default=0).items()})
        return datetime.now(tz) + delta

    dt = datetime.fromisoformat(value)  # We let the ValueError propogate
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt


@interactions.command()
async def remind(
    interaction: interactions.CommandInteraction,
    user_when: str = interactions.Option(
        name='datetime',
        description='The date and time to send the reminder. This can be relative.'
    )
) -> None:
    """Schedule a reminder to be sent at a specified time."""
    try:
        dt = parse_datetime(user_when)
    except ValueError:
        await interaction.respond(
            f'Could not parse the value of `datetime`: {user_when}', ephemeral=True,
        )
        return

    await interaction.respond(f'Created reminder to be sent <t:{dt.timestamp()}:R>...')
