import datetime
from decimal import Decimal

from hu import ObjectDict as OD
from mongoengine import DateField
from mongoengine import DecimalField
from mongoengine import DynamicDocument
from mongoengine import IntField
from mongoengine import StringField
from sheets import pull_data

DECIMAL_FIELDS = {
    "fte",
    "hired_fte",
    "target_fte",
    "actual_fte",
}  # This is a code smell


class TeamMember(DynamicDocument):
    item_id = IntField()
    name = StringField()
    firstname = StringField()
    lastname = StringField()
    chapter = StringField(null=True)
    squad = StringField(null=True)
    future_squad = StringField(null=True)
    chapter_lead = StringField(null=True)
    squad_lead = StringField(null=True)
    budget_holder = StringField(null=True)
    fte = DecimalField(precision=2, null=True, force_string=True)
    hired_fte = DecimalField(precision=2, null=True)
    target_fte = DecimalField(precision=2, null=True)
    actual_fte = DecimalField(precision=2, null=True)
    state = StringField(null=True)
    priority = StringField(null=True)
    startdate = DateField(null=True)
    enddate = DateField(null=True)
    location = StringField(null=True)
    notes = StringField(null=True)
    outsourcing_channel = StringField(null=True)
    outsourcing_oversight = StringField(null=True)
    personal_number = StringField(null=True)

    def __repr__(self):
        return f"<Team Member {self.item_id}: {self.name}>"

    __str__ = __repr__


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


months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def clean_int(tm, slot):
    val = tm[slot]
    tm[slot] = int(val) if val else None


def clean_name(tm):
    """
    Feeble attempt to normalise name representations.
    """
    words = tm["name"].split()
    tm["lastname"] = words[-1]
    tm["firstname"] = " ".join(words[:-1])


def clean_date(tm, slot):
    """
    Simple date conversion - note storage as a string here!
    """
    if not tm[slot]:
        tm[slot] = None
    else:
        d, m, y = tm[slot].replace("-", " ").split()
        tm[slot] = datetime.date(int(y) + 2000, months.index(m) + 1, int(d))


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
    data = load_data_rows(
        sheet_id="1yoxaa2k8Sed1DpnQAS05Of22QxGg4hf7CAiJcgr7BtQ", range_spec="Sheet 1"
    )
    print(data)
