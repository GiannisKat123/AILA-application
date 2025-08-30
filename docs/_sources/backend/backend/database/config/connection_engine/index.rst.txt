backend.database.config.connection_engine
=========================================

.. py:module:: backend.database.config.connection_engine

.. autoapi-nested-parse::

   Connection Engine (SQLAlchemy)

   Purpose
   -------
   Centralizes database initialization for the application:
   - Builds a secure SQLAlchemy connection URL from environment-backed settings.
   - Creates the Engine (connection pool + SQL execution entry point).
   - Defines shared MetaData for table and schema objects.
   - Exposes a Declarative Base class for ORM models.

   .. rubric:: Notes

   - Uses `URL.create(...)` to avoid hardcoding credentials and to keep configuration
     environment-driven (e.g., via `.env`, container secrets, or deployment vars).
   - Engine settings can be tuned per deployment (pool size, health checks, SSL).
   - All ORM models must inherit from `declarativeBase` to participate in schema reflection
     and enable ORM features.



Attributes
----------

.. autoapisummary::

   backend.database.config.connection_engine.connection_url
   backend.database.config.connection_engine.connection_engine
   backend.database.config.connection_engine.metadata
   backend.database.config.connection_engine.declarativeBase


Module Contents
---------------

.. py:data:: connection_url

   Constructs the SQLAlchemy connection URL using values from Settings.
   This ensures credentials and connection details are loaded securely from environment variables or a `.env` file.

.. py:data:: connection_engine
   :value: None


   Core interface to the database.
   Responsible for managing connections, executing SQL, and pooling.

   :type: Engine object

.. py:data:: metadata

   Stores schema-level information about tables, constraints, indexes, etc. Shared across all models.

   :type: Metadata object

.. py:data:: declarativeBase

   Root class for ORM models.
   All model classes should inherit from this to gain ORM features and automatic schema generation.

   :type: Declarative Base

