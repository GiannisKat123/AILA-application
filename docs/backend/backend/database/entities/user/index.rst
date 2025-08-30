backend.database.entities.user
==============================

.. py:module:: backend.database.entities.user

.. autoapi-nested-parse::

   User ORM Model
   ==============

   The ``User`` ORM model represents a registered user in the system. It maps to the
   ``app_user`` table and contains authentication, verification, and role information.

   Key features
   ~~~~~~~~~~~~
   - PostgreSQL-native UUID primary key (``id``)
   - Username, password, and session token storage
   - User role management (e.g., ``admin``, ``member``)
   - Email verification with codes and timestamps
   - Verification state tracking



Classes
-------

.. autoapisummary::

   backend.database.entities.user.User


Module Contents
---------------

.. py:class:: User(user_name: str, password: str, role: str, email: str, verification_code: str, date_created_on, session_id: str)

   Bases: :py:obj:`backend.database.config.connection_engine.declarativeBase`


   ORM model for the `app_user` table.
   Represents a registered user in the system.

   .. attribute:: id

      Primary key. Unique identifier for the user.

      :type: UUID

   .. attribute:: user_name

      Username chosen by the user (max 255 chars).

      :type: str

   .. attribute:: password

      Hashed password of the user.

      :type: str

   .. attribute:: session_id

      Current session token for the user.

      :type: str

   .. attribute:: role

      Role of the user (e.g., "admin", "member").

      :type: str

   .. attribute:: email

      Email address of the user.

      :type: str

   .. attribute:: verified

      Whether the user's email has been verified.

      :type: bool

   .. attribute:: verification_code

      Code sent to the user for verification.

      :type: str

   .. attribute:: code_created_on

      Timestamp when the verification code was generated.

      :type: datetime


   .. py:attribute:: __tablename__
      :value: 'app_user'



   .. py:attribute:: id
      :type:  sqlalchemy.orm.Mapped[uuid.UUID]

      Primary key. UUID of the user.


   .. py:attribute:: user_name
      :type:  sqlalchemy.orm.Mapped[str]

      Username of the user (max length 255).


   .. py:attribute:: password
      :type:  sqlalchemy.orm.Mapped[str]

      Hashed password of the user.


   .. py:attribute:: session_id
      :type:  sqlalchemy.orm.Mapped[str]

      Session token string associated with the user.


   .. py:attribute:: role
      :type:  sqlalchemy.orm.Mapped[str]

      Role assigned to the user (e.g., admin, member).


   .. py:attribute:: email
      :type:  sqlalchemy.orm.Mapped[str]

      Email address of the user (max length 255).


   .. py:attribute:: verified
      :type:  sqlalchemy.orm.Mapped[bool]

      Boolean flag indicating if the user has been verified.


   .. py:attribute:: verification_code
      :type:  sqlalchemy.orm.Mapped[str]

      Verification code used for confirming user identity.


   .. py:attribute:: code_created_on
      :type:  sqlalchemy.orm.Mapped[datetime.datetime]

      Datetime when the verification code was created. Defaults to current UTC time.


   .. py:method:: __str__() -> str

      Return a human-readable string representation of the user.

      :returns: A formatted string containing the user ID, username, and (hashed) password.
      :rtype: str



