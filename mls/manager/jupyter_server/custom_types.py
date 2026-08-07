"""Локальные custom types для CLI Jupyter Server."""
from mls.manager.notebook_service.cli import GroupedOption as CustomGroupedOption


class ManifestOptions(CustomGroupedOption):
    """Опции манифеста."""

    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = 3


class RequiredOptions(CustomGroupedOption):
    """Обязательные опции запуска."""

    GROUP: str = 'Опции обязательные'
    GROUP_INDEX = -10000


class CreateOptions(CustomGroupedOption):
    """Опции создания."""

    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = 3


class ResumeOptions(CustomGroupedOption):
    """Опции возобновления."""

    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = 3


class ListOptions(CustomGroupedOption):
    """Опции списка."""

    GROUP: str = 'Опции дополнительные:'
    GROUP_INDEX = 3


class ModifyOptions(CustomGroupedOption):
    """Опции изменения."""

    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = 3


class AutoShutdownOptions(CustomGroupedOption):
    """Опции управления автовыключением."""

    GROUP: str = 'Опции дополнительные'
    GROUP_INDEX = 3
