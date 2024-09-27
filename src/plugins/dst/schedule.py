from nonebot import require
from nonebot import logger

from . import config
from .database import add_or_update_servers
from .klei import get_server_list

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

server_list: list[dict[str, any]] = list()
new_server_list: list[dict[str, any]] = list()

# @scheduler.scheduled_job("cron", minute="*/1", id="update_server_list")
@scheduler.scheduled_job("cron", second="*/20", id="update_server_list")
def update_server_list():
    global new_server_list
    new_server_list = get_server_list(config.region, config.platform)
    if type(new_server_list) is str:
        logger.error(new_server_list)
        return
    if len(new_server_list) == 0:
        logger.warning("更新服务器列表为空!")
        return
    global server_list
    server_list = new_server_list
    try:
        logger.debug(f"成功读取 {len(server_list)} 个服务器, 数据更新中")
        add_or_update_servers(server_list)
    except Exception as e:
        logger.error("更新服务器状态异常 {}", e)

# @scheduler.scheduled_job("cron", second="*/5", id="demo")
# def demo():
#     logger.debug(len(server_list))