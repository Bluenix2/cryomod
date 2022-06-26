# This class isn't used by anything directly, but importing it causes it to be
# registered as a convertor which is used by starlette.
from .converters import SnowflakeConvertor
