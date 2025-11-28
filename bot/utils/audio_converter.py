"""Audio format conversion (MP3 → OGG OPUS)."""
import logging
import subprocess
from pathlib import Path
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


class AudioConverter:
    """Converts audio formats using FFmpeg."""

    def __init__(self):
        self.temp_dir = Path("/app/data/.audio_cache")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def convert_to_ogg(self, mp3_path: str) -> str:
        """
        Convert audio to OGG OPUS format.
        Supports MP3, M4A, WAV, and already-opus formats (.ogg, .opus).
        Returns path to converted file.
        """
        mp3_file = Path(mp3_path)
        if not mp3_file.exists():
            raise FileNotFoundError(f"Audio file not found: {mp3_path}")

        # Check if already in OGG/OPUS format - no conversion needed
        if mp3_file.suffix.lower() in [".ogg", ".opus"]:
            logger.info(f"File already in OPUS format: {mp3_path}")
            return mp3_path

        # Use hash of original file as cache key
        ogg_path = self.temp_dir / f"{mp3_file.stem}.ogg"

        if ogg_path.exists():
            logger.info(f"Using cached conversion: {ogg_path}")
            return str(ogg_path)

        try:
            # FFmpeg conversion command
            cmd = [
                "ffmpeg",
                "-i", str(mp3_file),
                "-c:a", "libopus",
                "-b:a", "128k",
                "-y",  # Overwrite output
                str(ogg_path)
            ]

            logger.info(f"Converting {mp3_path} to OGG OPUS format...")

            # Run conversion asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {stderr.decode()}")

            logger.info(f"Successfully converted: {mp3_path} → {ogg_path}")
            return str(ogg_path)

        except asyncio.TimeoutError:
            logger.error(f"Conversion timeout for: {mp3_path}")
            raise
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise
