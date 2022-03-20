"""
test_load_data.py: Not technically a unit test, and can therefore
be migrated to integration testing in the future as proper unit
tests increase confidence in integrity sufficiently that integration
testing is only required in CI, where it doesn't slow developers
down too much.
"""
from sheets import load_data_rows
from models import PeriodData

def test_spreadsheet_load():
    """

    """
    data = load_data_rows(
        sheet_id='1yFZLLz2Juln2s5nz26HcEPXOMMNbubeyPophqOIStFI',
        range_spec='data!A8:C19',
        item_type=PeriodData
    )

