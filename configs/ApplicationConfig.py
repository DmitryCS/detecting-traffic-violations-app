from .config import Config
from db.config import SQLiteConfig, PostgresConfig
from transport.sanic.config import SanicConfig


class ApplicationConfig:
    my_config: Config

    def __init__(self):
        self.my_config = Config()
        self.sanic = SanicConfig()
        # self.database = SQLiteConfig()
        self.database = PostgresConfig()
