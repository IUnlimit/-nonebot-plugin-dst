from pydantic import BaseModel

from .model import Platform


class Config(BaseModel):
    """Plugin Config Here"""
    region: str = "ap-east-1"
    platform: str = Platform.Steam.value
    token: str = "pds-g^KU_AQ9RWZZB^GBRTQFNi+PU4Kf/c0HYhcr0K80pZSG/wSKPTKpgKwOg="

    dst_mysql_user: str = "root"
    dst_mysql_password: str = "123456"
    dst_mysql_host: str = "127.0.0.1"
    dst_mysql_port: int = 3306
    dst_mysql_database: str = "dst"