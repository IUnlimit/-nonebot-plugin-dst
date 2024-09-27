from sqlalchemy import create_engine, Engine, select

from nonebot import require
from nonebot import logger
from sqlalchemy.orm import sessionmaker, Session, lazyload
from tqdm import tqdm

from . import config
from .klei import get_lobby_list
from .utils import copy_non_empty_fields, safe_get
from .model import Base, ModInfo, ServerInfo, ServerDetail, ServerSecondaries, LobbyRead

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
    engine = create_engine(f"sqlite:///{path}", echo=False, future=True, connect_args={"check_same_thread": False})
    # engine = create_engine(f"mysql+pymysql://{config.dst_mysql_user}:{config.dst_mysql_password}@{config.dst_mysql_host}:{config.dst_mysql_port}/{config.dst_mysql_database}")
    new_session = sessionmaker(bind=engine)
    # ModInfo.__table__.drop(bind=engine)
    # ServerInfo.__table__.drop(bind=engine)
    # ServerDetail.__table__.drop(bind=engine)
    # ServerSecondaries.__table__.drop(bind=engine)
    # LobbyRead.__table__.drop(bind=engine)
    Base.metadata.create_all(engine)

def add_or_update(session: Session, model, unique_key: str, **kwargs):
    """
    Add a new instance of model or update an existing one based on primary key.

    :param session: SQLAlchemy session object
    :param model: SQLAlchemy model class
    :param kwargs: Attributes of the model as keyword arguments
    """
    # query
    instance = session.query(model).filter_by(**{unique_key: kwargs[unique_key]}).first()

    if instance:
        # update
        for key, value in kwargs.items():
            setattr(instance, key, value)
        session.add(instance)
    else:
        # add
        instance = model(**kwargs)
        session.add(instance)
        session.flush()

    return instance

def is_need_update(row_id: str, session: Session) -> ServerInfo:
    return (session.query(ServerInfo)
     .options(lazyload(ServerInfo.detail), lazyload(ServerInfo.secondaries))
     .filter_by(row_id = row_id).first())

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

def add_lobby_read(info: ServerInfo, session: Session):
    # TODO 数据库仅存储最新的数据，redis 里存历史数据（1d）
    lobby_list = get_lobby_list(config.region, info.row_id, config.token)
    if type(lobby_list) == str:
        if lobby_list == "E_NOT_IN_DB":
            return
        logger.error("获取房间信息失败, 未知原因: {}", lobby_list)
        return
    if len(lobby_list) != 1:
        logger.error("异常的 lobby_list 长度: {}, {}", len(lobby_list), lobby_list)
        return
    lobby = lobby_list[0]
    lobby_read = LobbyRead(
        info_id=info.id,
        data=lobby.get("data"),
        world_gen=lobby.get("worldgen"),
        players=lobby.get("players"),
        desc=lobby.get("desc"),
        tick=lobby.get("tick"),
        client_mod_soff=lobby.get("clientmodsoff"),
        nat=lobby.get("nat")
    )
    exist = True
    if not info.lobby_read:
        info.lobby_read = lobby_read
        exist = False
    else:
        copy_non_empty_fields(lobby_read, info.lobby_read, ['data', 'worldgen', 'players', 'desc', 'tick', 'clientmodsoff', 'nat'])

    if 'mods_info' in lobby:
        temp_list = list()
        try:
            for row in list(lobby.get('mods_info')):
                # 本地模组将不被收录
                if type(row) == str and str(row).startswith("workshop-"):
                    temp_list = list()
                elif type(row) == bool:
                    mod_info = ModInfo(
                        workshop=safe_get(temp_list, 0),
                        display_name=safe_get(temp_list, 1),
                        v1=safe_get(temp_list, 2),
                        v2=safe_get(temp_list, 3)
                    )

                    if not info.lobby_read.mods_info:
                        info.lobby_read.mods_info = []
                    # exist = session.query(ModInfo).filter_by(workshop=mod_info.workshop).first()
                    exist = session.execute(select(ModInfo).where(ModInfo.workshop == mod_info.workshop)).scalar_one_or_none()

                    if not exist:
                        info.lobby_read.mods_info.append(mod_info)
                    else:
                        copy_non_empty_fields(mod_info, exist, ['workshop', 'display_name', 'v1', 'v2'])
                        session.merge(exist)
                        session.flush()
                    continue
                temp_list.append(row)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("更新模组列表异常, mods_info: {}", lobby.get('mods_info'), e)

def add_secondaries(info: ServerInfo, session: Session, secondaries_dict: dict[str, dict[str, any]]):
    if secondaries_dict is not None:
        try:
            for key, value in secondaries_dict.items():
                secondaries = ServerSecondaries(
                    info_id=info.id,
                    world=key,
                    secondaries_id=value.get("id"),
                    addr=value.get("__addr"),
                    steam_id=value.get("steamid"),
                    port=value.get("port"),
                )
                if not info.secondaries:
                    info.secondaries = []
                
                exist = session.execute(select(ServerSecondaries).where(ServerSecondaries.secondaries_id == secondaries.secondaries_id)).scalar_one_or_none()
                if not exist:
                    info.secondaries.append(secondaries)
                else:   
                    copy_non_empty_fields(secondaries, exist, ['secondaries_id', 'addr', 'steam_id', 'port'])
                    session.merge(exist)
                    session.flush()
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("更新 secondaries 列表异常, secondaries: {}", secondaries_dict, e)

def add_or_update_servers(server_list: list[dict[str, any]]):
    session = new_session()
    for server in tqdm(server_list):
        exist = True
        info = session.query(ServerInfo).filter_by(row_id=server.get("__rowId")).first()
        if info is None:
            info = ServerInfo(row_id=server.get("__rowId"))
            session.add(info)
            session.flush()
            exist = False

        detail = get_server_detail(info.id, server)
        if not exist:
            info.detail = detail
        else:
            copy_non_empty_fields(detail, info.detail, ['addr', 'host', 'clan_only', 'platform', 'mods', 'name', 'pvp', 'session', 'fo', 'password', 'guid', 'max_connections', 'dedicated', 'client_hosted', 'owner_net_id', 'connected', 'mode', 'port', 'v', 'tags', 'season', 'lan_only', 'intent', 'allow_new_players', 'server_paused', 'steam_id', 'steam_room'])

        add_lobby_read(info, session)
        add_secondaries(info, session, server.get("secondaries"))
        
        # TODO 分批提交, 多线程
    session.commit()
