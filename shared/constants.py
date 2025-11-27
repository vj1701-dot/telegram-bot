"""Application constants."""
from enum import Enum


class AudioFormat(str, Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    OGG = "ogg"
    WAV = "wav"
    M4A = "m4a"


SUPPORTED_FORMATS = {f".{f.value}" for f in AudioFormat}
DEFAULT_OPUS_BITRATE = "128k"
LOG_ROTATION_SIZE = 10_000_000  # 10MB
MAX_BACKUP_COUNT = 5
DEFAULT_DATA_DIR = "/app/data"
