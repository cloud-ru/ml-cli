"""Общая настройка api-клиентов."""
import os

MAX_RETRIES: int = int(os.getenv('MLS_MAX_RETRIES', 5))
BACKOFF_FACTOR: float = float(os.getenv('MLS_BACKOFF_FACTOR', 3.0))
CONNECT_TIMEOUT: int = int(os.getenv('MLS_MAX_RETRIES', 10))
READ_TIMEOUT: int = int(os.getenv('MLS_READ_TIMEOUT', 10 * 60))
SSL_VERIFY: bool = os.getenv('MLS_SSL_VERIFY', 'true') in ('t', 'true', 'True')
