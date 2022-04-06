"""
test_mongo.py: discovery and learning around mongoengine.
"""
from decimal import Decimal

import pytest
from mongoengine import connect
from mongoengine import DecimalField
from mongoengine import disconnect
from mongoengine import Document
from mongoengine import StringField
from mongoengine import ValidationError
from pytest import raises
from transformers.sheets import clean_percentage


class Doc1(Document):
    f1 = DecimalField(precision=2)


class Doc2(Document):
    f1 = DecimalField(precision=2, required=True)


class Doc3(Document):
    f1 = DecimalField(precision=2, null=True)


@pytest.mark.parametrize(["doc"], [(Doc1,), (Doc2,), (Doc3,)])
def test_decimal(doc):
    """
    Test understanding of Decimal fields."""
    connect(uuidRepresentation="pythonLegacy")
    doc.objects.delete()
    d1 = doc(f1=Decimal("9.99"))
    d2 = doc(f1="99.99")
    d1.save()
    d2.save()
    assert len(list(doc.objects.all())) == 2
    disconnect()


def save_null():
    connect(uuidRepresentation="pythonLegacy")
    Doc2.objects.delete()
    d2 = Doc2(f1=None)
    d2.save()
    disconnect()


def test_required():
    "Test that None values don't actually get saved for required fields."
    connect(uuidRepresentation="pythonLegacy")
    Doc1.objects.delete()
    d1 = Doc1(f1=None)
    d1.save()
    assert raises(ValidationError, save_null)
    disconnect()


zero = Decimal(0)


@pytest.mark.parametrize(("value", "result"), (("0%", zero), ("100%", Decimal("1"))))
def test_clean_percentage(value, result):
    d1 = {"name": "d1", "x": value}
    clean_percentage(d1, "x")


def test_record_manipulation():
    class ThreeFields(Document):
        f1 = DecimalField()
        f2 = DecimalField()
        f3 = StringField(required=False)

    connect(uuidRepresentation="pythonLegacy")
    ThreeFields.objects.delete()
    r1 = ThreeFields(f1=Decimal("1.23"), f2="2.34")
    r1.save()
    assert r1.f2 == Decimal("2.34")
    assert r1.f3 is None
    r1.update(f1=Decimal("5.67"))
    assert r1.f2 == Decimal("2.34")
    r1.update(f2=2.34)
    assert r1.f2 == Decimal("2.34")
    disconnect()


if __name__ == "__main__":
    test_required()
