from starlette.convertors import Convertor, register_url_convertor
from wumpy.models import Snowflake

__all__ = ['SnowflakeConvertor']


class SnowflakeConvertor(Convertor[Snowflake]):
    """Path parameter convertor for Discord Snowflakes."""

    regex = "[0-9]+"

    def convert(self, value: str) -> Snowflake:
        return Snowflake(int(value))

    def to_string(self, value: Snowflake) -> str:
        return str(value)


register_url_convertor('snowflake', SnowflakeConvertor())
