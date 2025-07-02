from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import MetaData
from backend.database.config.config import settings

connection_url = URL.create(
    drivername=settings.DB_DRIVER_NAME,
    username=settings.DB_USERNAME,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    database=settings.DB_DATABASE_NAME
)

connection_engine = create_engine(connection_url)

metadata = MetaData()

declarativeBase = declarative_base(metadata=metadata)

