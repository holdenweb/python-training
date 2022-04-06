import json

from transformers.sheets import build_service


def test_service():
    with build_service() as service:
        assert hasattr(service, "spreadsheets")
        sheet = service.spreadsheets()
        assert hasattr(sheet, "get")
        assert "get" in dir(sheet)
        result = sheet.get(
            spreadsheetId="1yoxaa2k8Sed1DpnQAS05Of22QxGg4hf7CAiJcgr7BtQ"
        ).execute()
        assert type(result) is dict
        for i, sheet in enumerate(result["sheets"], 1):
            print(i, sheet["properties"]["title"])


if __name__ == "__main__":
    test_service()
