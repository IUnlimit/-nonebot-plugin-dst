from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config
from .model import Platform

REGION = "ap-east-1"
PLATFORM: str = Platform.Steam.value
TOKEN = "pds-g^KU_AQ9RWZZB^GBRTQFNi+PU4Kf/c0HYhcr0K80pZSG/wSKPTKpgKwOg="

__plugin_meta__ = PluginMetadata(
    name="dst",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

from .schedule import scheduler





