"""Модуль openssl.

Реализует методы шифрования/дешифрования совместимые с openssl.

шифрование аналогично:
    > openssl aes-256-cbc -pbkdf2 -a

дешифрование аналогично:
    > openssl aes-256-cbc -pbkdf2 -a -d

параметры шифрования используют значения принятые в openssl по умолчанию:
    -iter 10000
    -salt
    -saltlen 8

используется 48 байтный ключ (derived key) вида:
    первые 32 байта - ключ шифрования, следующие 16 байт - вектор инициализации для AES.

структура зашифрованного сообщения openssl:
    Salted__[соль][сообщение выравненное по блокам в 16 байт].

сообщения закодировано в base64 c длинной строки 64 байта.
"""
import base64
import os
from functools import partial
from itertools import islice

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

from mls.utils.execption import DecryptionError
from mls.utils.execption import EncryptionError


KEY_LENGTH = 32
IV_LENGTH = 16
ITERATIONS = 10000
PADDING_BLOCK_SIZE = 16
SALT_LENGTH = 8
SALTED_LITERAL = b'Salted__'
OUTPUT_LINE_LENGTH = 64


# генерация ключа (derived key) вида KEY+IV, где KEY - ключ шифрования, IV - вектор инициализации AES
_get_dkey = partial(PBKDF2, dkLen=KEY_LENGTH + IV_LENGTH, count=ITERATIONS, hmac_hash_module=SHA256)


def _format_output(data: bytes) -> bytes:
    """Форматирование вывода в соответствии с форматом openssl.

    :param data: Данные для форматирования.
    """
    def batch(iterable, size):
        it = iter(iterable)
        while item := bytes(islice(it, size)):
            yield item

    result = batch(data, OUTPUT_LINE_LENGTH)

    return b'\n'.join(result) + b'\n'


def encrypt(data: str, password: str) -> bytes:
    """Шифрует данные с использованием сгенерированного ключа.

    Возвращает зашифрованные данные в формате base64

    :param data: Данные для шифрования.
    :param password: Пароль для генерации ключа.
    """
    salt = os.urandom(SALT_LENGTH)
    dkey = _get_dkey(password.encode('utf-8'), salt)
    key = dkey[:KEY_LENGTH]
    iv = dkey[KEY_LENGTH:]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        padded_data = pad(data.encode('utf-8'), PADDING_BLOCK_SIZE)
        encrypted_data = cipher.encrypt(padded_data)
    except (ValueError, UnicodeError) as e:
        raise EncryptionError('Unable to encrypt data') from e

    result = base64.b64encode(SALTED_LITERAL + salt + encrypted_data)

    return _format_output(result)


def decrypt(msg: bytes, password: str) -> str:
    """Расшифровывает данные с использованием сгенерированного ключа.

    :param msg: Зашифрованное сообщение в формате base64.
    :param password: Пароль для генерации ключа.
    """
    try:
        data = base64.b64decode(msg)
    except ValueError as e:
        raise DecryptionError('Invalid input data') from e

    if data[:len(SALTED_LITERAL)] != SALTED_LITERAL:
        raise DecryptionError('Invalid message structure')

    data = data.removeprefix(SALTED_LITERAL)
    salt = data[:SALT_LENGTH]
    dkey = _get_dkey(password.encode('utf-8'), salt)
    key = dkey[:KEY_LENGTH]
    iv = dkey[KEY_LENGTH:]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    encrypted_data = data[SALT_LENGTH:]

    try:
        padded_data = cipher.decrypt(encrypted_data)
        return str(unpad(padded_data, PADDING_BLOCK_SIZE).decode('utf-8'))
    except ValueError as e:
        raise DecryptionError('Unable to decrypt data') from e
