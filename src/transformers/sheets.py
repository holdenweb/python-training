import os
import pickle
import sys

from decimal import Decimal
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from hu import ObjectDict as OD

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


def clean_percentage(tm, slot):
    """
    Simple percentage conversion: stored as a Decimal to 2DP.
    """
    if not tm[slot]:
        tm[slot] = None
    else:
        if tm[slot][-1] != "%":
            raise ValueError(f"Row for '{tm.name}' has invalid percentage for {slot}")
        tm[slot] = Decimal(tm[slot][:-1]) / Decimal(100).quantize(Decimal("0.01"))


def clean_data_row(tm):
    """
    Fix up the fields from raw to structured form.

    This should be refactored to be a part of whatever plugin or
    class goes with the data source. With luck there'll be a
    barrage of data cleaning methods that can be easily deloyed.
    """
    p = tm["period"]
    tm["period"] = f"{p[-2:]}{months.index(p[:3])+1:02d}"
    tm["total_pay"] = Decimal(tm["total_pay"]).quantize(Decimal(".01"))
    tm["regular_pay"] = Decimal(tm["regular_pay"]).quantize(Decimal(".01"))


def clean_column_name(name):
    if name:
        name = name.lower().replace(" ", "_")
        for char in "/?+=":
            name = name.replace(char, "")
        while "__" in name:
            name = name.replace("__", "_")
        return "item_id" if name == "id" else name
    else:
        return "unknown"  # The column with an unknown purpose


def clean_row(r, n_cols):
    """
    Add necessary null string values to pad row to required length.
    """
    return r + [""] * (n_cols - len(r))


def load_data_rows(sheet_id, range_spec, item_type):
    """
    Transform a range in a spreadsheet into a list of row dictionaries.

    This is an implementation-specific function, so maybe it shoould be a
    document method. Ideally most records will have enough semantic
    content (eventually) that a standard load method will suffice.
    """
    raw_data_rows = pull_data(sheet_id, range_spec)["values"]
    col_names = [clean_column_name(name) for name in raw_data_rows[0]]
    n_cols = len(col_names)
    del raw_data_rows[0]
    # The line below ignores blank rows and those with no column 1 This is
    # pretty arbitrary, and should ideally be somehow configurable per data
    # source
    data_rows = [clean_row(r, n_cols) for r in raw_data_rows if len(r) > 1 and r[1]]
    data_rows = [r[: len(col_names)] for r in data_rows]
    data_rows = [OD(dict(zip(col_names, slot))) for slot in data_rows]
    for row in data_rows:
        yield item_type.from_dict(row)


if __name__ == "__main__":
    sys.exit("Test code required!")
