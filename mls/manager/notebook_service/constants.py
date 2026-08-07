"""Shared constants for Jupyter Server and TensorBoard CLI modules."""

CREATE_REQUIRED_FIELDS = (
    'name',
    'image.name',
    'image.tag',
    'image.type',
    'instance_type',
)

CREATE_ALLOWED_FIELDS = (
    'name',
    'image',
    'instance_type',
    'region',
    'allocation_name',
    'queue_name',
    'description',
    'pause_at',
    'postponed_pause_enabled',
    's3_buckets',
    's3_credentials',
)
