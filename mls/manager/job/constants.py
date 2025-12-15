"""Модуль содержит константы приложения для задач обучения."""
from mls.utils.settings import REGIONS

priority = 'low', 'medium', 'high'
table_sort_filter_fields = 'gpu_count', 'instance_type', 'job_desc', 'job_name'
job_types = 'binary', 'horovod', 'pytorch', 'pytorch2', 'pytorch_elastic', 'binary_exp'
cluster_keys = ['A100-MT', 'SR003', 'SR004', 'SR005', 'SR006', 'SR008'] + REGIONS
job_statuses = 'Completed', 'Completing', 'Deleted', 'Failed', 'Pending', 'Running', 'Stopped', 'Succeeded', 'Terminated'
job_actions_in_fail = 'delete', 'restart'
