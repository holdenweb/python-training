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




if __name__ == "__main__":
    data = load_data_rows(
        sheet_id="1yoxaa2k8Sed1DpnQAS05Of22QxGg4hf7CAiJcgr7BtQ", range_spec="Sheet 1"
    )
    print(data)
