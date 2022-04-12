import json
import csv

from mongoengine import connect
from mongoengine import DecimalField
from mongoengine import DynamicDocument
from mongoengine import StringField

from team import clean_int
from sheets import clean_column_name


def as_dict(md):
    result = json.loads(md.to_json())
    clean_int(result, "period")
    return result


def compare_docs(c: DynamicDocument, i: dict):
    kc = c._data.keys()
    ki = i._data.keys()
    common = kc & ki
    deleted = kc - ki
    added = ki - kc
    return common, deleted, added


def report_changes(current, incoming, id_fields=None):
    changes = {}
    common, absent, added = compare_docs(current, incoming)
    common -= {"id"}  # XXX hack
    absent -= {
        "_id",
        "id",
        "_cls",
    }  # incoming record has no _id as not yet saved. We must pray for it.
    output = []
    add = output.append  # Readability abbreviation
    #
    # Major semantic difference here between treating a field's absence as a
    # request for deletion of the key or simply the absence of an instruction
    # to effect change. In the former case the updated record exactly mirrors
    # the incoming record, whereas in the latter the incoming record is best
    # regarded as updates to the existing record.
    #
    # The current code implements only the first strategy, but it would be
    # much better to offer the user a configurable choice of strategies.
    #
    # Note: identifying fields are required. It would be sensible for each
    #       model definition to nominate a default set of id fields.
    headers = [
        "=" * 80,
        *(show_field(name, current, incoming) for name in id_fields),
        "-" * 80,
    ]
    if absent:
        add("Deleted fields:")
        for k in absent:
            add(f"{k}: {current[k]!r}")
            changes[k] = None
    if added:
        add("New fields:")
        for k in added:
            add(f"{k}: {incoming[k]!r}")
            changes[k] = incoming[k]
    if any(current[k] != incoming[k] for k in common):
        add("Modified fields:")
        for k in common:
            cv = current[k]
            iv = incoming[k]
            if cv != iv:
                add(show_field(k, current, incoming))
                changes[k] = incoming[k]
    if output:
        print("  \n".join(headers + output))
    return changes


def show_field(name, this, other):
    if this[name] == other[name]:
        return f"{name}: {this[name]}"
    else:
        return f"{name}: {this[name]} -> {other[name]}"


MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


if __name__ == "__main__":
    """
    Load some sample data.
    """

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

    def load_data_rows(header_row_number, item_type):
        with open('../../data/average_weekly_earnings.csv', newline='', encoding='utf-8-sig') as csvfile:
            for i in range(header_row_number - 1):
                next(csvfile, None)

            reader = csv.DictReader(csvfile)
            reader.fieldnames = [clean_column_name(name) for name in reader.fieldnames]

            for row in reader:
                if row["period"]:
                    yield item_type.from_dict(row)


    """
    The merge algorithm assumes stably ordered data.
    """
    incoming_stream = load_data_rows(header_row_number=7, item_type=PeriodData)
    incoming = next(incoming_stream)

    """
    We read the existing data in the same order as the incoming rows.
    When a key exists but is not present in the incoming stream there's
    a choice to be made (currently it's hardwired to assume the record
    is unchanged.) This means we can inset and update records, but not
    delete them.
    """
    with connect("WebDB"):
        new = edits = unchanged = 0
        current_stream = iter(PeriodData.objects.order_by("period"))
        for current in current_stream:
            # Copy any lower keys in the incoming stream as new records
            while current.period > incoming.period:
                print(f"New  item ({incoming.period})")
                new += 1
                incoming.save()
                try:
                    incoming = next(incoming_stream)
                    continue
                except StopIteration:
                    break
            #
            # If periods match it might be an update.
            # If they don't, the current record isn't in the
            # incoming stream and should be left or deleted
            # according to strategy (see below).
            #
            if current.period == incoming.period:
                changes = report_changes(current, incoming, id_fields=["period"])
                if changes:
                    edits += 1
                    current.update(**changes)
                else:
                    unchanged += 1
                try:
                    incoming = next(incoming_stream)
                except StopIteration:
                    break
            else:
                #
                # Here there's the option to leave items rather than
                # delete them if they don't appear in the incoming stream.
                # We currently leave them.
                #
                unchanged += 1
        else:  # We ran out of currents: any remaning incomings are new
            incoming.save()
            new += 1
            for incoming in incoming_stream:
                new += 1
                incoming.save()
    print(f"Team load: new: {new}, unchanged: {unchanged}, changes: {edits}")
