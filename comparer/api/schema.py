from marshmallow import Schema, fields, ValidationError
from marshmallow.fields import Field

from comparer.db.schema import ShopUnitType

UPDATE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class ImportNode(Schema):
    id = fields.UUID(required=True)
    name = fields.String(required=True)
    parentId = fields.UUID(required=False)
    type = fields.Method(deserialize="to_shop_unit_type", required=True)
    price = fields.Integer(required=False, allow_none=True, strict=True)

    @classmethod
    def to_shop_unit_type(cls, value):
        try:
            return ShopUnitType(value)
        except ValueError as error:
            raise ValidationError("Value must be 'OFFER' or 'CATEGORY'") from error


class Import(Schema):
    items = fields.List(Field, required=True)
    updateDate = fields.DateTime(format=UPDATE_DATE_FORMAT)
