import json
from decimal import Decimal
from typing import Optional

import mongoengine
import uvicorn
import wtforms
import wtforms.fields as ff
from fastapi import FastAPI
from fastapi import Form as apiForm
from fastapi.responses import HTMLResponse
from fields import DecimalField
from fields import StringField
from mongoengine import connect
from mongoengine import Document as BaseDocument
from multidict import MultiDict
from pydantic import BaseModel
from pydantic.main import ModelMetaclass
from wtforms import Form


me = mongoengine


class MyDocument(BaseDocument):  # Note: this should be different from subclassing
    """
    The MyDocument class is a simple refinement of the mongoengine Document class
    that adds methods to produce pydantic models and WTForms forms.
    """

    meta = {"allow_inheritance": True}

    @classmethod
    def model(self):
        """
        Return a pydantic model corresponding to the Mongo document.
        """
        annos = {}
        defaults = {}
        for name, field in self._fields.items():
            if name in {"id", "_cls"}:
                continue
            ft = type(field)
            if ft is StringField:
                anno = str
            elif ft is DecimalField:
                anno = Decimal
            else:
                raise TypeError(f"Cannot handle {ft!r} objects as MyDocument fields")
            if not field.required:
                anno = Optional[anno]
            if field.default:
                defaults[name] = field.default
            annos[name] = anno
        result = ModelMetaclass(
            "ItemPlus", (BaseModel,), dict(__annotations__=annos, **defaults)
        )
        return result

    @classmethod
    def form(self):
        """
        Return a WTForms form corresponding to the Mongo document.
        """
        fields = {}
        for name, field in self._fields.items():
            if name in {"id", "_cls"}:
                continue
            ft = type(field)
            kwargs = {}
            # Handle common arguments here?
            if ft is StringField:
                field_type = ff.StringField
            elif ft is DecimalField:
                field_type = ff.DecimalField
                kwargs["places"] = field.precision
            else:
                raise TypeError(f"Cannot generate form fields for {ft!r} objects")
            # kwargs.update(field.widget_args)
            fields[name] = field_type(**kwargs)
        result = wtforms.form.FormMeta("SyntheticItemForm", (Form,), fields)
        return result


class MongoItem(MyDocument):
    name = StringField(required=True, unique=True)
    description = StringField()
    price = DecimalField(default=Decimal("9.99"), precision=2)


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Decimal("99.99")


ItemPlus = MongoItem.model()

connect("MongoItems")
app = FastAPI()


@app.get("/items/")
def list_items():
    """
    Sample GET method returns all the items stored.
    """
    return [json.loads(o.to_json()) for o in MongoItem.objects.all()]


@app.post("/items/")
def create_item(item: ItemPlus):
    """
    Sample POST method adds input to MongoDB after conversion to a suitable
    Document subclass.

    uvicorn POST methods take a dictionary (constructed from input of type
    'application/json') and convert it into the type annotated in the
    function signature. This ensures that only valid objects can be created.
    Note that uvicorn appears happy to accept a dictionary.
    """
    MongoItem(**item.dict()).save()
    return item.dict()


class ItemForm(Form):
    name = ff.StringField("Label for name")
    description = ff.StringField("Label for description")
    price = ff.DecimalField("Label for price", places=2)


@app.post("/items/form_action")
def process_form(
    name: str = apiForm(...),
    description: str = apiForm(...),
    price: Decimal = apiForm(...),
):
    print(name, description, price)
    item = Item(name=name, description=description, price=price)
    form = MongoItem.form()(
        MultiDict({"name": name, "description": description, "price": price})
    )
    print(form.validate())
    return item


@app.get("/items/form/{item_id}")
def input_form(item_id: str):
    """
    Paints a fairly primitive form as a proof of concept.

    In real life we'd use something like jinja and bootstrap to produce
    industrial-strength HTML, but these technologies are well-established.
    This at least proves the concept is viable.
    """
    print(item_id)
    result = MongoItem.objects(name=item_id).get()
    d = {k: getattr(result, k) for k in result._fields if k not in {"_cls", "id"}}
    # form = ItemForm(MultiDict(d))
    form = MongoItem.form()(MultiDict(d))
    return paint_form(form)


@app.get("/items/form/")
def empty_input_form():
    print("Bare form")
    form = MongoItem.form()()
    return paint_form(form)


def paint_form(form):
    form_from = f"""
<html><body>
<h1>The Form</h1>
<form action="/items/form_action" method="POST">
{form.name.widget(form.name)}<br/>
{form.description.widget(form.description)}<br/>
{form.price.widget(form.price)}<br/>
<input type="submit">
</form>
</body></html>
"""
    return HTMLResponse(form_from)


@app.get("/items/{item_id}.json")
def item_as_json(item_id: str):
    """
    Takes path argument, returns JSON.
    """
    result = MongoItem.objects(name=item_id).get()
    return json.loads(result.to_json())


@app.post("/items/{item_id}")
@app.get("/items/{item_id}")
def item_for_display(item_id: str) -> HTMLResponse:
    """
    Takes path argument, returns HTML.
    """
    result = MongoItem.objects(name=item_id).get()
    return HTMLResponse(
        f"<html><body><h1>{result.description}</h1>"
        f"<p>{result.name}: {result.price}</p></body></html>"
    )


if __name__ == "__main__":
    uvicorn.run(app)
