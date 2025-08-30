backend.database.config
=======================

.. py:module:: backend.database.config

.. autoapi-nested-parse::

   The `config` package provides two core building blocks for establishing and managing database connections.

   Contents:
       - config: Configuration layer - strongly typed app settings loaded from environment variables (with .env support), exposed through a singleton Settings object
       - connection_engine: Database layer - SQLAlchemy bootstrap that constructs a connection URL from those settings, creates the Engine, shared MetaData, and the declarative base for ORM models

   Together they provide secure, environment-driven configuration and a clean ORM foundation.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /backend/backend/database/config/config/index
   /backend/backend/database/config/connection_engine/index


