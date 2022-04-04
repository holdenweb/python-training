"""
Module fields:

This was an experiment in creating document types that merge mongoengine
methods with pydantic and other interfaces.
"""
import sys
import mongoengine.fields as mf
import wtforms as wtf

# wrap all mongoengine field types to accept widget args by creating sub
# classes of the original mongoengine fields, with the same name as those in
# mongoengine.

field_type_names = mf.__all__
this_module = sys.modules[__name__]

class FieldMixin:
    """
    This class defines additional behaviours common to all augmented fields.
    As a minimum, each field needs to be able to render itself in a form.
    Eventually I imagine each field_type will have a default field type.

    For the present I'm prepared to define everything in excruciating detail
    if I have to. Later the default widgets can be injected into the type call.

    The methods will be used by the upgraded Document class to render forms.
    """
    def render(self):
        print(f"I'm a {self.__class__.__name__}")

for field_type_name in field_type_names:
    # Load the field type from mongoengine.fields
    field_type = getattr(mf, field_type_name)
    # Create a new class, mixing in the required widget behaviours
    new_class = type(field_type)(field_type_name, (field_type, FieldMixin), {"default_widget_class": wtf.StringField})
    # and store it under the same name
    setattr(this_module, field_type_name, new_class)

if __name__ == '__main__':
    sf = StringField(w_args=dict(a=1, hello='world'))
    sf.render()
