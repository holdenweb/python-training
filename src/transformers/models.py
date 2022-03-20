from mongoengine import DynamicDocument, StringField, DecimalField


class PeriodData(DynamicDocument):
    period = StringField()
    total_pay = DecimalField()
    regular_pay = DecimalField()

    @classmethod
    def clean_period(cls, s):
        return f"{s[-2:]}{MONTHS.index(s[:3])+1:02d}"

    @classmethod
    def from_dict(cls, d):
        """
        Take input from a citionary and return a PeriodData instance.

        Ideally here we'd go through pydantic for validation,
        but at present I'm focusing on the haoppy paths..
        """
        period = cls.clean_period(d["period"])
        return cls(
            period=period, regular_pay=d["regular_pay"], total_pay=d["total_pay"]
        )

