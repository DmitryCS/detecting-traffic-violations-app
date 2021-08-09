import os
from dotenv import load_dotenv

load_dotenv()


class SQLiteConfig:
    name = os.getenv('dbname', 'db2.sqlite')
    url = rf'sqlite:///{name}'


class PostgresConfig:
    name = os.getenv('POSTGRES_DB', 'detections')
    user = os.getenv('POSTGRES_USER', 'user1')
    password = os.getenv('POSTGRES_PASSWORD', 'qwerty')
    host = os.getenv('POSTGRES_HOST', '0.0.0.0')
    port = os.getenv('POSTGRES_PORT', '5432')
    url = rf'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'


'''
alembic init
alembic revision --message="add progress" --autogenerate
alembic upgrade head

sudo service postgresql restart
sudo -u postgres psql postgres
DROP DATABASE detections;
CREATE DATABASE detections;
CREATE USER user1 WITH PASSWORD 'qwerty';
GRANT ALL PRIVILEGES ON DATABASE "detections" to user1;

\c detections;
truncate videos_queue cascade;
'''
