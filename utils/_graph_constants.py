"""Constants shared across GraphClient mixin modules."""

LARGE_FILE_THRESHOLD = 4 * 1024 * 1024  # 4 MB
UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB — must be a multiple of 320 KB
