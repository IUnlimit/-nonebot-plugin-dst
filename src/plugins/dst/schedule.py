from nonebot import require
from nonebot import logger

from . import REGION, PLATFORM
from .api import get_server_list

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

server_list = list()
new_server_list = list()

@scheduler.scheduled_job("cron", second="*/15", id="update_server_list")
def update_server_list():
    global new_server_list
    new_server_list = get_server_list(REGION, PLATFORM)
    if type(new_server_list) is str:
        logger.error(new_server_list)
        return
    if len(new_server_list) == 0:
        logger.warning("更新服务器列表为空!")
        return
    global server_list
    server_list = new_server_list
    logger.debug(f"成功更新 {len(server_list)} 个服务器")

@scheduler.scheduled_job("cron", second="*/5", id="demo")
def demo():
    logger.debug(len(server_list))