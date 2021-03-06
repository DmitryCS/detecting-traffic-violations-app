from sqlalchemy import create_engine

from configs.ApplicationConfig import ApplicationConfig
from context import Context
from db.database import DataBase


def init_db_sqlite(config: ApplicationConfig, context: Context):
    engine = create_engine(
        name_or_url=config.database.url,
        pool_pre_ping=True,     # if session dropped, it'll automatically launched
    )
    database = DataBase(connection=engine)
    database.check_connection()

    context.set('database', database)
