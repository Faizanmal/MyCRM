"""
Encrypted Model Fields
=======================
Transparent Django model fields that encrypt data before persisting to database
and decrypt upon retrieval, keeping database dumps free of plaintext.
"""
from django.db import models

from core.encryption import encrypt_value, decrypt_value, is_encrypted


class EncryptedCharField(models.CharField):
    """
    CharField that automatically encrypts values on write and decrypts on read.
    Raw SQL queries and database dumps only expose ciphertext.
    """

    def get_prep_value(self, value):
        val = super().get_prep_value(value)
        if val is not None and val != '':
            if not is_encrypted(str(val)):
                return encrypt_value(str(val))
        return val

    def from_db_value(self, value, expression, connection):
        if value is not None and is_encrypted(value):
            return decrypt_value(value)
        return value

    def to_python(self, value):
        if value is not None and is_encrypted(value):
            return decrypt_value(value)
        return super().to_python(value)


class EncryptedTextField(models.TextField):
    """
    TextField that automatically encrypts values on write and decrypts on read.
    Raw SQL queries and database dumps only expose ciphertext.
    """

    def get_prep_value(self, value):
        val = super().get_prep_value(value)
        if val is not None and val != '':
            if not is_encrypted(str(val)):
                return encrypt_value(str(val))
        return val

    def from_db_value(self, value, expression, connection):
        if value is not None and is_encrypted(value):
            return decrypt_value(value)
        return value

    def to_python(self, value):
        if value is not None and is_encrypted(value):
            return decrypt_value(value)
        return super().to_python(value)
