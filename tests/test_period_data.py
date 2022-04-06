from transformers.models import PeriodData


def test_repr():
    p = PeriodData.from_dict(dict(period="Jan 01"))
    assert repr(p).startswith("Jan 01")
    p = PeriodData.from_dict(dict(period="Dec 21", total_pay=345, regular_pay=234))
    assert repr(p) == "Dec 21, total_pay=345.00, regular_pay=234.00"
