backend.api.models
==================

.. py:module:: backend.api.models

.. autoapi-nested-parse::

   Pydantic models used for request/response validation and API data contracts.

   Each class defines the structure of data expected in API endpoints, ensuring
   validation and automatic OpenAPI schema generation.



Classes
-------

.. autoapisummary::

   backend.api.models.UserCredentials
   backend.api.models.ConversationCreationDetails
   backend.api.models.UpdateConversationDetails
   backend.api.models.NewMessage
   backend.api.models.UserOpenData
   backend.api.models.Message
   backend.api.models.UserAuthentication
   backend.api.models.UserData
   backend.api.models.VerifCode
   backend.api.models.UserFeedback


Module Contents
---------------

.. py:class:: UserCredentials(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents login credentials for a user.


   .. py:attribute:: username
      :type:  str

      The username of the user


   .. py:attribute:: password
      :type:  str

      The plaintext password provided for authentication.


.. py:class:: ConversationCreationDetails(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents details needed to create a new conversation.


   .. py:attribute:: username
      :type:  str

      The username of the conversation owner.


   .. py:attribute:: conversation_name
      :type:  str

      A human-readable title for the conversation.


.. py:class:: UpdateConversationDetails(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents details required to update an existing conversation.


   .. py:attribute:: conversation_name
      :type:  str

      New name/title for the conversation.


   .. py:attribute:: conversation_id
      :type:  str

      Unique identifier of the conversation to update.


.. py:class:: NewMessage(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents a new message to be created in a conversation.


   .. py:attribute:: feedback
      :type:  bool | None

      Optional feedback flag (True/False, None if unset).


   .. py:attribute:: id
      :type:  str

      Unique identifier of the message.


   .. py:attribute:: conversation_id
      :type:  str

      The ID of the conversation the message belongs to.


   .. py:attribute:: text
      :type:  str

      The text content of the message.


   .. py:attribute:: role
      :type:  str

      The role of the sender (e.g., 'user', 'assistant', 'system').


.. py:class:: UserOpenData(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Publicly shareable user data (non-sensitive).


   .. py:attribute:: email
      :type:  str

      User's email address.


   .. py:attribute:: username
      :type:  str

      User's username.


.. py:class:: Message(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents a message sent in an API request (e.g., chat interaction).


   .. py:attribute:: message
      :type:  str

      The current message being sent.


   .. py:attribute:: conversation_history
      :type:  List[dict]

      History of previous messages in the conversation.


.. py:class:: UserAuthentication(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Authentication response returned after login attempts.


   .. py:attribute:: authenticated
      :type:  bool

      Whether the authentication was successful.


   .. py:attribute:: detail
      :type:  str

      Additional information or error message.


   .. py:attribute:: user_details
      :type:  UserCredentials | None

      User details if authenticated, otherwise None.


.. py:class:: UserData(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents data required to register a new user.


   .. py:attribute:: username
      :type:  str

      Desired username.


   .. py:attribute:: password
      :type:  str

      Password chosen by the user.


   .. py:attribute:: email
      :type:  str

      Email address of the user.


.. py:class:: VerifCode(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents a request to verify a user's email.


   .. py:attribute:: username
      :type:  str

      Username associated with the verification code.


   .. py:attribute:: code
      :type:  str

      Verification code provided by the user.


.. py:class:: UserFeedback(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents feedback on a user message.


   .. py:attribute:: message_id
      :type:  str

      The ID of the message being reviewed.


   .. py:attribute:: conversation_id
      :type:  str

      The conversation to which the message belongs.


   .. py:attribute:: feedback
      :type:  bool | None

      Feedback value (True=positive, False=negative, None=unset).


