from django.db.models import Model
from rest_framework import serializers
from api.models import Element, Isotope


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)



def all_fields(model):
    return [symbol for symbol in dir(model)
            if not symbol.startswith('_') and symbol not in dir(Model)
            and symbol not in ('DoesNotExist', 'MultipleObjectsReturned')]


class ElementSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Element
        fields = all_fields(Element)
        read_only_fields = all_fields(Element)


class IsotopeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Isotope
        fields = all_fields(Isotope)
        read_only_fields = all_fields(Isotope)

