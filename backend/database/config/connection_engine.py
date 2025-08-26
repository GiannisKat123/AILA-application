from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import MetaData
from backend.database.config.config import settings

# --------------------------------------------------------------------
# Construct the SQLAlchemy connection URL using values from Settings.
# This ensures credentials and connection details are loaded securely
# from environment variables or a `.env` file.
# --------------------------------------------------------------------
connection_url = URL.create(
    drivername=settings.DB_DRIVER_NAME,   # e.g., "postgresql", "mysql", "sqlite"
    username=settings.DB_USERNAME,        # Database username
    password=settings.DB_PASSWORD,        # Database password
    host=settings.DB_HOST,                # Hostname or IP of the DB server
    database=settings.DB_DATABASE_NAME    # Name of the database
)

# --------------------------------------------------------------------
# Engine object: core interface to the database.
# Responsible for managing connections, executing SQL, and pooling.
# --------------------------------------------------------------------
connection_engine = create_engine(connection_url)

# --------------------------------------------------------------------
# Metadata object: stores schema-level information about tables,
# constraints, indexes, etc. Shared across all models.
# --------------------------------------------------------------------
metadata = MetaData()

# --------------------------------------------------------------------
# Declarative Base: root class for ORM models.
# All model classes should inherit from this to gain ORM features
# and automatic schema generation.
# --------------------------------------------------------------------
declarativeBase = declarative_base(metadata=metadata)
