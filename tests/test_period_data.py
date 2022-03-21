from models import PeriodData

def test_repr():
    p = PeriodData(period="Jan 01")
    assert repr(p).startswith("Jan 01")
