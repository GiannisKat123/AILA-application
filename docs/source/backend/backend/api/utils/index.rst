backend.api.utils
=================

.. py:module:: backend.api.utils

.. autoapi-nested-parse::

   JWT utilities for issuing and verifying access tokens.

   Functions
   ---------
   create_access_token(data: dict) -> str
       Creates a signed JWT access token with an expiration (`exp`) claim.
   verify_token(token: str) -> str | None
       Verify a JWT's signature & expiration and return the subject (`sub`) if valid.

   Environment contract (from `settings`)
   --------------------------------------
   SECRET_KEY : str
       HMAC signing key for JWTs.
   ALGORITHM : str
       JWT signing algorithm (e.g., "HS256").
   ACCESS_TOKEN_EXPIRE_MINUTES : int
       Token lifetime window in minutes.



Functions
---------

.. autoapisummary::

   backend.api.utils.create_access_token
   backend.api.utils.verify_token


Module Contents
---------------

.. py:function:: create_access_token(data: dict) -> str

   Create a signed JWT access token.

   :param data: Claims to embed in the token
                Retrieves it in `verify_token` function.
   :type data: dict

   :returns: Encoded JWT string.
   :rtype: str

   .. rubric:: Notes

   - Adds an `exp` (expiration) claim calculated from ACCESS_TOKEN_EXPIRE_MINUTES.
   - Uses `settings.SECRET_KEY` and `settings.ALGORITHM` for signing.


.. py:function:: verify_token(token: str) -> Optional[str]

   Verify a JWT and return its subject.


   :param token: Encoded JWT string from the client (e.g., cookie or Authorization header).
   :type token: str

   :returns: The `sub` claim (subject) if the token is valid, otherwise None.
   :rtype: str | None

   .. rubric:: Notes

   - Decodes and validates the signature and expiration using SECRET_KEY/ALGORITHM.
   - Returns `payload.get('sub')` for downstream authentication logic.
   - On any JWTError (invalid signature, expired, malformed), returns None.


