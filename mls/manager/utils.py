"""Общие утилиты подпакета ``mls.manager`` (например чтение YAML для CLI)."""
import click
import yaml  # type: ignore


def read_yaml(file_path: str):
    """Читает YAML-файл и возвращает распарсенное значение.

    Args:
        file_path: Путь к файлу.

    Returns:
        Результат yaml.safe_load (обычно dict).

    Raises:
        click.ClickException: При ошибке чтения или парсинга.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise click.ClickException(f"Ошибка чтения YAML-файла '{file_path}': {e}")
