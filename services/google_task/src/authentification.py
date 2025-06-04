import datetime
import json
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class CredentialsManager:
    """Handle loading and refreshing Google API credentials."""

    def __init__(self, token_path: str) -> None:
        self.token_path = token_path
        self.credentials: Credentials = self._load_credentials()

    def _load_credentials(self) -> Credentials:
        with open(self.token_path, "r") as token_file:
            creds_data = json.load(token_file)
        return Credentials.from_authorized_user_info(creds_data)

    def refresh_if_needed(self) -> Credentials:
        """Refresh the credentials if they have expired."""
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
            with open(self.token_path, "w") as token_file:
                token_file.write(self.credentials.to_json())
        return self.credentials

    def token_ttl(self) -> Optional[int]:
        """Return the remaining time-to-live of the token in seconds."""
        if self.credentials.expiry:
            expiry_aware = self.credentials.expiry.replace(
                tzinfo=datetime.timezone.utc
            )
            now_aware = datetime.datetime.now(tz=datetime.timezone.utc)
            return int((expiry_aware - now_aware).total_seconds())
        print("No expiry information available for the token.")
        return None
