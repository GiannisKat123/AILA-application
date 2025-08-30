backend.crypt
=============

.. py:module:: backend.crypt

.. autoapi-nested-parse::

   The `crypt` package provides cryptographic utilities that secure
   authentication workflows and user data.

   It centralizes password hashing, password validation, and verification
   code generation in order to enforce consistent security practices
   across the application.

   Contents
   --------
   - encrypt_decrypt
       Utility module exposing the `EncryptionDec` class:
           * `hash_password` — securely hashes plaintext passwords using bcrypt
           * `check_passwords` — verifies a plaintext password against a hashed one
           * `is_valid_password` — validates password complexity rules:
               - minimum length (8+)
               - must include lowercase, uppercase, digit, and special character
           * `generate_verification_code` — produces numeric verification codes (default length: 6 digits) for email verification or 2FA workflows



Submodules
----------

.. toctree::
   :maxdepth: 1

   /backend/backend/crypt/encrypt_decrypt/index


Classes
-------

.. autoapisummary::

   backend.crypt.EncryptionDec


Package Contents
----------------

.. py:class:: EncryptionDec

   Utility class for password hashing, validation, and verification code generation.

   .. method:: hash_password(text: str) -> str

      Hashes a plaintext password using bcrypt with a generated salt.

   .. method:: check_passwords(plain_text: str, passwd: str) -> bool

      Verifies a plaintext password against a hashed password.

   .. method:: is_valid_password(password: str) -> bool

      Validates that a password meets security requirements:
      - At least 8 characters
      - At least one lowercase letter
      - At least one uppercase letter
      - At least one digit
      - At least one special character

   .. method:: generate_verification_code(length: int = 6) -> str

      Generates a numeric verification code of given length (default: 6 digits).



   .. py:method:: hash_password(text: str) -> str

      Hash a plaintext password using bcrypt.

      :param text: The plaintext password.
      :type text: str

      :returns: The bcrypt-hashed password (UTF-8 decoded).
      :rtype: str



   .. py:method:: check_passwords(plain_text: str, passwd: str) -> bool

      Verify if a plaintext password matches a hashed password.

      :param plain_text: The plaintext password to check.
      :type plain_text: str
      :param passwd: The previously hashed password to verify against.
      :type passwd: str

      :returns: True if the password matches, False otherwise.
      :rtype: bool



   .. py:method:: is_valid_password(password: str) -> bool

      Validate that a password meets security complexity rules.

      :param password: The plaintext password to validate.
      :type password: str

      :returns: True if password is valid, False otherwise.
      :rtype: bool

      .. rubric:: Notes

      - Minimum length: 8 characters
      - Must contain at least:
        - one lowercase letter
        - one uppercase letter
        - one digit
        - one special character (!@#$%^&*(),.?":{}|<>)



   .. py:method:: generate_verification_code(length: int = 6) -> str

      Generate a numeric verification code of specified length.

      :param length: Number of digits in the code. Default is 6.
      :type length: int, optional

      :returns: A randomly generated numeric code of given length.
      :rtype: str

      .. rubric:: Example

      >>> enc = EncryptionDec()
      >>> enc.generate_verification_code()
      '493027'



