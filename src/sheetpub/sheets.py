import os
import pickle
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = os.environ.get(
    "CREDENTIALS_FILE", os.path.expanduser("~/.credentials.json")
)

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

DEBUG_FEATURE_FLAGS = {"parse"}

#
# Should we connect to the MongoDB on import?     🤷
#


def debug(debug_class, *arg, **kw):
    if debug_class in DEBUG_FEATURE_FLAGS or "all" in DEBUG_FEATURE_FLAGS:
        print(*arg, **kw)


def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds


def build_service():
    creds = authenticate()
    service = build("sheets", "v4", credentials=creds)
    return service


def pull_data(sheet_id, range):
    ss_service = build_service()

    # Retrieve the spreadsheet's contents from the Sheets service.
    document = (
        ss_service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range)
        .execute()
    )
    return document


def pull_props(sheet_id):
    ss_service = build_service()
    return ss_service.spreadsheets().get(spreadsheetId=sheet_id).execute()


if __name__ == "__main__":
    sys.exit("Test code required!")
