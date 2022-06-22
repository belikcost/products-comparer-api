import functools
import math
import operator
from datetime import datetime

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from comparer.db.schema import ShopUnitType
from comparer.utils.get_children_dates import get_children_dates
from comparer.utils.get_children_prices import get_children_prices

UPDATE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class BaseNode(Schema):
    id = fields.UUID(required=True)
    name = fields.String(required=True)

    class Meta:
        ordered = True


class ImportNode(BaseNode):
    parent_id = fields.UUID(data_key='parentId', allow_none=True)
    type = EnumField(ShopUnitType, required=True, by_value=True)
    price = fields.Integer(allow_none=True, strict=True)


class Import(Schema):
    items = fields.List(fields.Nested(ImportNode), required=True)
    update_date = fields.DateTime(format=UPDATE_DATE_FORMAT, required=True, data_key="updateDate")


class GetNode(BaseNode):
    type = EnumField(ShopUnitType, required=True, by_value=True)
    date = fields.Method("date_serializer")
    price = fields.Method('price_serializer')
    parent_id = fields.UUID(required=True, allow_none=True, data_key="parentId")
    children = fields.Method('children_serializer')

    @classmethod
    def date_serializer(cls, obj):
        if obj.get('date'):
            date = obj['date']
        else:
            date = max(get_children_dates(obj))

        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.000Z')
        return date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    @classmethod
    def price_serializer(cls, obj):
        if obj['type'] == ShopUnitType.offer.value:
            return obj['price']

        children_prices = get_children_prices(obj)
        if len(children_prices) == 0:
            return None

        average = functools.reduce(operator.add, children_prices, 0) / len(children_prices)
        return math.floor(average)

    @classmethod
    def children_serializer(cls, obj):
        if obj['type'].value == ShopUnitType.offer.value:
            return None
        return obj['children']

    class Meta:
        ordered = True
