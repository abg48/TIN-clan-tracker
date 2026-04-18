import os
import gspread
import uuid
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

VALID_ITEMS_SHEET = 'Item DB'
EVENT_LOG_SHEET = 'Event Log'

def _get_credentials() -> Credentials:
    account_info = {
        "type": "service_account",
        "project_id": os.environ["GOOGLE_PROJECT_ID"],
        "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
        "private_key": os.environ["GOOGLE_PRIVATE_KEY"].replace('\\n', '\n'),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    return Credentials.from_service_account_info(account_info, scopes=SCOPES)

def get_sheet(sheet_name: str):
    client = gspread.authorize(_get_credentials())
    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

def log_item(item_name: str, user: str, timestamp: str, team: str):
    drop_id = str(uuid.uuid4())[:8]
    sheet = get_sheet(EVENT_LOG_SHEET)
    sheet.append_row([drop_id, timestamp, user, item_name, team])
    return drop_id

def undo_item(drop_id: str):
    sheet = get_sheet(EVENT_LOG_SHEET)
    rows = sheet.get_all_values()
    for i, row in enumerate(rows):
        if row and row[0] == drop_id:
            sheet.delete_rows(i + 1)
            return True
    return False


class EventItemCache:
    def __init__(self):
        self.items: list[str] = []
        self.last_sync: datetime | None = None

    def sync_items(self):
        sheet = get_sheet(VALID_ITEMS_SHEET)
        self.items = [row[0] for row in sheet.get_all_values() if row and row[0]]
        self.last_sync = datetime.utcnow()

    def get_items(self) -> list[str]:
        return self.items
    
item_cache = EventItemCache()