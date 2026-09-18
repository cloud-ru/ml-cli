"""Модуль содержит константы приложения для задач обучения."""
from mls.utils.settings import REGIONS as USER_CLUSTERS

CLOUD_CLUSTERS = ['SR003', 'SR004', 'SR005', 'SR006', 'SR008', 'SR009']

priority = 'low', 'medium', 'high'
table_sort_filter_fields = 'gpu_count', 'instance_type', 'job_desc', 'job_name'
job_types = 'binary', 'horovod', 'pytorch', 'pytorch2', 'torchrun', 'pytorch_elastic', 'binary_exp'
cluster_keys = (CLOUD_CLUSTERS + USER_CLUSTERS) if USER_CLUSTERS else CLOUD_CLUSTERS
job_statuses = 'Completed', 'Completing', 'Deleted', 'Failed', 'Pending', 'Running', 'Stopped', 'Succeeded', 'Terminated'
job_actions_in_fail = 'delete', 'restart'
