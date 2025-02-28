"""Общая настройка api-клиентов."""
import os

MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', 5))
BACKOFF_FACTOR: float = float(os.getenv('BACKOFF_FACTOR', .2))
CONNECT_TIMEOUT: int = int(os.getenv('MAX_RETRIES', 10 * 60))
READ_TIMEOUT: int = int(os.getenv('READ_TIMEOUT', 10))
