"""Тестовые сценарии для проверки методов шифрования/дешифрования модуля openssl."""
from typing import Callable

import pytest

from mls.manager.configure import utils
from mls.manager.configure.utils import configure_profile
from mls.utils import openssl
from mls.utils.execption import ConfigWriteError
from mls.utils.execption import DecryptionError

PLAIN_DATA = 'Test data to be encrypted. Текст на кириллице 😁'
PASSWORD = 'пароль'


def test_encrypt_decrypt_success():
    """Проверка успешного шифрования/дешифрования."""
    encrypted_data = openssl.encrypt(PLAIN_DATA, PASSWORD)
    assert encrypted_data != PLAIN_DATA

    decrypted_data = openssl.decrypt(encrypted_data, PASSWORD)
    assert decrypted_data == PLAIN_DATA


def test_invalid_password():
    """Проверка на расшифровку с неверным паролем."""
    encrypted_data = openssl.encrypt(PLAIN_DATA, PASSWORD)

    with pytest.raises(DecryptionError):
        openssl.decrypt(encrypted_data, 'wrong_password')


def test_decrypt_invalid_msg():
    """Проверка на расшифровку невалидного сообщения."""
    with pytest.raises(DecryptionError):
        openssl.decrypt(b'wrong encrypted message', PASSWORD)


def test_openssl_compat():
    """Проверка на совместимость с openssl.

    Пытается расшифровать строку, зашифрованную командой
        > openssl aes-256-cbc -pbkdf2 -a
    """
    openssl_msg = b'''U2FsdGVkX18rDWPsrMzcsp18DJFADyvWxC5foVu5B2Y735vBCrk/snguwqMEa92y
KQQrbmCjGo4b7cjCLQ4d55xiEZutkbUM+Nq0CJM0cXPjFspsU8Tpp6BFFZD8n1jC'''

    decrypted_data = openssl.decrypt(openssl_msg, PASSWORD)
    assert decrypted_data == PLAIN_DATA


def test_encrypted_credentials_file_exists(monkeypatch):
    """Тест вызова encrypt когда файл существует."""
    monkeypatch.setattr('os.path.exists', lambda x: True)
    monkeypatch.setattr(utils, 'get_decrypt_password', lambda: 'decrypted_password')
    encrypt_password_called = False

    def mock_get_encrypt_password():
        nonlocal encrypt_password_called
        encrypt_password_called = True

    monkeypatch.setattr(utils, 'get_encrypt_password', mock_get_encrypt_password)
    monkeypatch.setattr(utils, 'prepare_profile', lambda *args, **kwargs: (None, None))
    monkeypatch.setattr(utils, 'collect_user_inputs', lambda *args, **kwargs: None)
    monkeypatch.setattr(utils, 'save_profile', lambda *args, **kwargs: None)

    configure_profile(encrypt=True)

    assert not encrypt_password_called


def test_exception_handling(monkeypatch):
    """Имитация вызова ошибки при записи."""
    def mock_save_profile(config, credentials, password):
        raise Exception('Sample error')

    monkeypatch.setattr(utils, 'save_profile', mock_save_profile)

    mock_click_echo: Callable = lambda message: None
    monkeypatch.setattr(utils.click, 'echo', mock_click_echo)
    monkeypatch.setattr(utils, 'prepare_profile', lambda *args, **kwargs: (None, None))
    monkeypatch.setattr(utils, 'collect_user_inputs', lambda *args, **kwargs: None)
    with pytest.raises(ConfigWriteError):
        configure_profile()
