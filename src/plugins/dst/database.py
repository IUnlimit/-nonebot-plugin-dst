from sqlalchemy import create_engine, Engine

from nonebot import require
from nonebot import logger
from sqlalchemy.orm import sessionmaker, Session, load_only, lazyload

from . import REGION, TOKEN
from .klei import get_lobby_list
from .model import Base, ServerInfo, ServerDetail, ServerSecondaries, LobbyRead

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store

SQLITE_FILENAME = "dst.sqlite3"

# 获取插件数据目录
data_dir = store.get_plugin_data_dir()
engine: Engine
new_session: sessionmaker[Session]
batch = 100

def init_db():
    path = str(data_dir.absolute()) + '/' + SQLITE_FILENAME
    logger.info("SQLite file initialized with path {}", path)
    global engine, new_session
    engine = create_engine(f"sqlite:///{path}")
    new_session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

def is_need_update(row_id: str, session: Session) -> bool:
    info = (session.query(ServerInfo)
     .options(lazyload(ServerInfo.detail), lazyload(ServerInfo.secondaries))
     .filter_by(row_id = row_id).first())
    return info is None

def get_server_detail(info_id: int, server: dict[str, any]) -> ServerDetail:
    return ServerDetail(
        info_id=info_id,
        addr=server.get("__addr"),
        host=server.get("host"),
        clan_only=server.get("clanonly"),
        platform=server.get("platform"),
        mods=server.get("mods"),
        name=server.get("name"),
        pvp=server.get("pvp"),
        session=server.get("session"),
        fo=server.get("fo"),
        password=server.get("password"),
        guid=server.get("guid"),
        max_connections=server.get("maxconnections"),
        dedicated=server.get("dedicated"),
        client_hosted=server.get("clienthosted"),
        owner_net_id=server.get("ownernetid"),
        connected=server.get("connected"),
        mode=server.get("mode"),
        port=server.get("port"),
        v=server.get("v"),
        tags=server.get("tags"),
        season=server.get("season"),
        lan_only=server.get("lanonly"),
        intent=server.get("intent"),
        allow_new_players=server.get("allownewplayers"),
        server_paused=server.get("serverpaused"),
        steam_id=server.get("steamid"),
        steam_room=server.get("steamroom"),
    )

def add_lobby_read(info_id: int, row_id: str, session: Session):
    lobby_list = get_lobby_list(REGION, row_id, TOKEN)
    if type(lobby_list) == str:
        logger.error("获取房间信息失败: {}", lobby_list)
        return
    for lobby in lobby_list:
        pass

def add_or_update_servers(server_list: list[dict[str, any]]):
    session = new_session()
    for server in server_list:
        info = ServerInfo(
            row_id=server.get("__rowId"),
        )
        if is_need_update(info.row_id, session) is False:
            continue

        session.add(info)
        # 刷新连接，给对象添加自增ID
        session.flush()

        session.add(get_server_detail(info.id, server))
        add_lobby_read(info.id, info.row_id, session)
        if server.get("secondaries") is not None:
            for key, value in server.get("secondaries").items():
                session.add(ServerSecondaries(
                    info_id=info.id,
                    world=key,
                    addr=value.get("__addr"),
                    secondaries_id=value.get("id"),
                    steam_id=value.get("steamid"),
                    port=value.get("port"),
                ))
    session.commit()
