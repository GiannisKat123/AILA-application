backend.database.config.config
==============================

.. py:module:: backend.database.config.config


Attributes
----------

.. autoapisummary::

   backend.database.config.config.settings


Classes
-------

.. autoapisummary::

   backend.database.config.config.Settings


Module Contents
---------------

.. py:class:: Settings(_case_sensitive: bool | None = None, _nested_model_default_partial_update: bool | None = None, _env_prefix: str | None = None, _env_file: pydantic_settings.sources.DotenvType | None = ENV_FILE_SENTINEL, _env_file_encoding: str | None = None, _env_ignore_empty: bool | None = None, _env_nested_delimiter: str | None = None, _env_nested_max_split: int | None = None, _env_parse_none_str: str | None = None, _env_parse_enums: bool | None = None, _cli_prog_name: str | None = None, _cli_parse_args: bool | list[str] | tuple[str, Ellipsis] | None = None, _cli_settings_source: pydantic_settings.sources.CliSettingsSource[Any] | None = None, _cli_parse_none_str: str | None = None, _cli_hide_none_type: bool | None = None, _cli_avoid_json: bool | None = None, _cli_enforce_required: bool | None = None, _cli_use_class_docs_for_groups: bool | None = None, _cli_exit_on_error: bool | None = None, _cli_prefix: str | None = None, _cli_flag_prefix_char: str | None = None, _cli_implicit_flags: bool | None = None, _cli_ignore_unknown_args: bool | None = None, _cli_kebab_case: bool | None = None, _secrets_dir: pydantic_settings.sources.PathType | None = None, **values: Any)

   Bases: :py:obj:`pydantic_settings.BaseSettings`


   Application configuration settings loaded from environment variables
   or a `.env` file. Provides strongly typed access to environment values.


   .. py:attribute:: OLLAMA_SERVER_URL
      :type:  str

      URL of the Ollama server for model inference.


   .. py:attribute:: FRONTEND_URL
      :type:  str

      Base URL of the frontend client application.


   .. py:attribute:: DB_USERNAME
      :type:  str

      Database username credential.


   .. py:attribute:: DB_PASSWORD
      :type:  str

      Database password credential.


   .. py:attribute:: DB_HOST
      :type:  str

      Hostname or IP address of the database server.


   .. py:attribute:: DB_DATABASE_NAME
      :type:  str

      Name of the application’s database.


   .. py:attribute:: DB_DRIVER_NAME
      :type:  str

      Database driver (e.g., `postgresql`, `mysql`, `sqlite`).


   .. py:attribute:: ACCESS_TOKEN_EXPIRE_MINUTES
      :type:  int

      Duration (in minutes) before access tokens expire.


   .. py:attribute:: API_KEY
      :type:  str

      OPEN API key for application-level integrations.


   .. py:attribute:: SECRET_KEY
      :type:  str

      Secret key used for signing tokens and securing sensitive operations.


   .. py:attribute:: ALGORITHM
      :type:  str

      Cryptographic algorithm used for JWT or token signing (e.g., `HS256`).


   .. py:attribute:: VITE_API_URL
      :type:  str

      API base URL injected into the frontend (e.g., Vite builds).


   .. py:attribute:: APP_PASSWORD
      :type:  str

      Application-specific password (e.g., for email sending).


   .. py:attribute:: SENDER_EMAIL
      :type:  str

      Default email address used for sending application emails.


   .. py:attribute:: COHERE_API_KEY
      :type:  str

      API key for accessing Cohere’s services.


   .. py:attribute:: COHERE_MODEL_ID
      :type:  str

      Identifier of the Cohere model to use.


   .. py:attribute:: INIT_MODE
      :type:  str

      Initialization mode (e.g., `dev`, `prod`, `test`).


   .. py:attribute:: OPEN_AI_MODEL
      :type:  str

      OpenAI model name (e.g., `gpt-4o-mini`).


   .. py:attribute:: TAVILY_API_KEY
      :type:  str

      API key for Tavily API integration.


   .. py:class:: Config

      Configuration for Pydantic settings. Loads values from `.env` file by default.


      .. py:attribute:: env_file
         :value: '.env'




.. py:data:: settings

   Defines a Settings object that contains the contents of the .env file

