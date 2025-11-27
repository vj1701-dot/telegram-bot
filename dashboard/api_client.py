"""HTTP client for bot API communication."""
import httpx
import logging
from typing import Optional, List, Dict
from dashboard.config import DashboardConfig

logger = logging.getLogger(__name__)


class BotAPIClient:
    """Communicates with bot API."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or DashboardConfig.BOT_API_URL
        self.timeout = 30.0

    def _get_client(self) -> httpx.Client:
        """Get synchronous HTTP client."""
        return httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def health_check(self) -> bool:
        """Check bot API health."""
        try:
            with self._get_client() as client:
                response = client.get("/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def send_audio(self, bot_token: str, chat_id: str, file_path: str) -> bool:
        """Send audio file."""
        try:
            with self._get_client() as client:
                response = client.post(
                    "/send-audio",
                    json={
                        "bot_token": bot_token,
                        "chat_id": chat_id,
                        "file_path": file_path
                    }
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Send audio failed: {e}")
            return False

    def send_by_date(self, bot_token: str, chat_id: str, date: str) -> Optional[Dict]:
        """Send all audio for a specific date."""
        try:
            with self._get_client() as client:
                response = client.post(
                    "/send-by-date",
                    json={
                        "bot_token": bot_token,
                        "chat_id": chat_id,
                        "date": date
                    }
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Send by date failed: {e}")
        return None

    def resend_audio(self, bot_token: str, chat_id: str, file_path: str) -> bool:
        """Resend audio file."""
        try:
            with self._get_client() as client:
                response = client.post(
                    "/resend-audio",
                    params={
                        "bot_token": bot_token,
                        "chat_id": chat_id,
                        "file_path": file_path
                    }
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Resend failed: {e}")
            return False

    def get_bot_status(self, bot_token: str) -> Optional[Dict]:
        """Get bot diagnostics."""
        try:
            with self._get_client() as client:
                response = client.get(f"/bot-status/{bot_token}")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Status check failed: {e}")
        return None

    def get_all_bot_status(self) -> List[Dict]:
        """Get status for all bots."""
        try:
            with self._get_client() as client:
                response = client.get("/bot-status-all")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Status check failed: {e}")
        return []

    def reload_config(self) -> bool:
        """Reload bot configuration."""
        try:
            with self._get_client() as client:
                response = client.post("/reload-config")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Config reload failed: {e}")
            return False

    def get_scheduler_jobs(self) -> Optional[Dict]:
        """Get scheduled jobs."""
        try:
            with self._get_client() as client:
                response = client.get("/scheduler-jobs")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
        return None

    def test_connection(self, bot_token: str) -> bool:
        """Test bot connection."""
        try:
            with self._get_client() as client:
                response = client.post(
                    "/test-connection",
                    params={"bot_token": bot_token}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
