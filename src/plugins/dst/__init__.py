from nonebot import get_plugin_config, logger
from nonebot.log import default_format, default_filter

logger.add("dst.log", level="INFO", format=default_format, filter=default_filter, rotation="1 day")

from nonebot.plugin import PluginMetadata

from .config import Config
config = get_plugin_config(Config)

from .database import init_db
from .schedule import scheduler

__plugin_meta__ = PluginMetadata(
    name="dst",
    description="",
    usage="",
    config=Config,
)

init_db()