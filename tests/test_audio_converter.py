"""Tests for audio converter."""
import pytest
import asyncio
from pathlib import Path
from bot.utils.audio_converter import AudioConverter


class TestAudioConverter:
    """Test audio conversion functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.converter = AudioConverter()

    @pytest.mark.asyncio
    async def test_converter_initialization(self):
        """Test converter initializes correctly."""
        assert self.converter.temp_dir.exists()

    @pytest.mark.asyncio
    async def test_ogg_file_passthrough(self, tmp_path):
        """Test that OGG files are not re-converted."""
        # Create a dummy OGG file
        ogg_file = tmp_path / "test.ogg"
        ogg_file.write_text("dummy content")

        result = await self.converter.convert_to_ogg(str(ogg_file))
        assert result == str(ogg_file)

    @pytest.mark.asyncio
    async def test_missing_file_raises_error(self):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            await self.converter.convert_to_ogg("/nonexistent/file.mp3")

    # Note: Full conversion tests require FFmpeg and actual MP3 files
    # These should be added for integration testing
