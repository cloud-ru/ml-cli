"""Модуль custom_types содержит определения пользовательских типов данных.

Эти типы данных кастомизированны в строчное представление для вывода в CLI
"""
from mls.utils.common_types import Choice

job_statuses = 'Completing', 'Deleted', 'Failed', 'Pending', 'Running', 'Stopped', 'Succeeded', 'Terminated'
output_formats = json, text = 'json', 'text'

job_choices = Choice(job_statuses)
output_choice = Choice(output_formats)
