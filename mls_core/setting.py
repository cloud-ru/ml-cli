"""Общая настройка api-клиентов."""
import os

MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', 5))
BACKOFF_FACTOR: float = float(os.getenv('BACKOFF_FACTOR', 3.0))
CONNECT_TIMEOUT: int = int(os.getenv('MAX_RETRIES', 10))
READ_TIMEOUT: int = int(os.getenv('READ_TIMEOUT', 10 * 60))
SSL_VERIFY: bool = os.getenv('SSL_VERIFY', 'true') in ('t', 'true', 'True')
