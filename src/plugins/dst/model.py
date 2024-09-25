from enum import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Text, BigInteger, ForeignKey, DateTime, func, Table
from sqlalchemy.orm import relationship


class Platform(Enum):
    Steam = "Steam"
    WeGame = "WeGame"
    Xbox = "Xbox"
    Switch = "Switch"
    PlayStation = "PlayStation"
    PS4Official = "PS4Official"

    def parse(self, _id: int):
        if _id == 1:
            return self.Steam
        elif _id == 2:
            return self.WeGame
        elif _id == 3:
            return self.Xbox
        elif _id == 4:
            return self.Switch
        elif _id == 5:
            return self.PlayStation
        elif _id == 6:
            return self.PS4Official
        else:
            return None

Base = declarative_base()
class ServerInfo(Base):
    __tablename__ = 'server_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 1 -> 1
    detail = relationship('ServerDetail', uselist=False)
    # 1 -> n
    secondaries = relationship('ServerSecondaries')  # secondaries list
    # 1 -> n
    lobbyRead = relationship('LobbyRead')
    row_id = Column(String(128), unique=True) # __rowId
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ServerDetail(Base):
    __tablename__ = 'server_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    info_id = Column(Integer, ForeignKey('server_info.id'))
    addr = Column(String(128)) # __addr
    host = Column(String(64)) # host
    clan_only = Column(Boolean) # clanonly
    platform = Column(Integer) # platform TODO
    mods = Column(Boolean) # mods
    name = Column(String(256)) # name
    pvp = Column(Boolean) # pvp
    session = Column(String(128)) # session
    fo = Column(Boolean) # fo
    password = Column(Boolean) # password
    guid = Column(String(128)) # guid
    max_connections = Column(Integer) # maxconnections
    dedicated = Column(Boolean) # dedicated
    client_hosted = Column(Boolean) # clienthosted
    owner_net_id = Column(String(128)) # ownernetid
    connected = Column(Integer) # connected
    mode = Column(String(64)) # mode
    port = Column(Integer) # port
    v = Column(Integer) # v
    tags = Column(Text) # tags
    season = Column(String(64)) # season
    lan_only = Column(Boolean) # lanonly
    intent = Column(String(64)) # intent
    allow_new_players = Column(Boolean) # allownewplayers
    server_paused = Column(Boolean) # serverpaused
    steam_id = Column(String(128)) # steamid
    steam_room = Column(String(128)) # steamroom
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ServerSecondaries(Base):
    __tablename__ = 'server_secondaries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    info_id = Column(Integer, ForeignKey('server_info.id'))
    world = Column(String(128))
    secondaries_id = Column(String(128)) # id
    addr = Column(String(128))  # __addr
    steam_id = Column(String(128))  # steamid
    port = Column(Integer)  # port
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

# 多对多
lobby_mod_association_table = Table('lobby_mod_association', Base.metadata,
    Column('lobby_id', Integer, ForeignKey('lobby_read.id')),
    Column('mod_id', Integer, ForeignKey('mod_info.id'))
)

class LobbyRead(Base):
    __tablename__ = 'lobby_read'

    id = Column(Integer, primary_key=True, autoincrement=True)
    info_id = Column(Integer, ForeignKey('server_info.id'))
    mod_info = relationship('ModInfo', secondary=lobby_mod_association_table)
    data = Column(Text) # data
    world_gen = Column(Text) # worldgen
    players = Column(Text) # players

class ModInfo(Base):
    __tablename__ = 'mod_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workshop = Column(String(128), unique=True) # [0]
    display_name = Column(String(128)) # [1]
    v1 = Column(String(128)) # [2]
    v2 = Column(String(128)) # [3]