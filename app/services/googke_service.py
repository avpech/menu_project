from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient import discovery

from app.core.config import settings

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


INFO = {
    'type': settings.type,
    'project_id': settings.project_id,
    'private_key_id': settings.private_key_id,
    'private_key': settings.private_key,
    'client_email': settings.client_email,
    'client_id': settings.client_id,
    'auth_uri': settings.auth_uri,
    'token_uri': settings.token_uri,
    'auth_provider_x509_cert_url': settings.auth_provider_x509_cert_url,
    'client_x509_cert_url': settings.client_x509_cert_url
}


CREDENTIALS = Credentials.from_service_account_info(
    info=INFO, scopes=SCOPES)


class GoogleService:
    """Взаимодействие с гугл таблицами."""

    def __init__(self) -> None:
        self.service = discovery.build('sheets', 'v4', credentials=CREDENTIALS)

    def read_values(self, spreadsheet_id: str) -> list[list[Any]]:
        """Прочитать данные из гугл-таблицы."""
        range = 'A1:G100'
        response = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueRenderOption='FORMULA'
        ).execute()
        return response.get('values', [])


google_service = GoogleService()
