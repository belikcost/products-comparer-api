from enum import unique, Enum

from sqlalchemy import MetaData, Table, Column, Integer, String, Date, ForeignKey, Enum as PgEnum

convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}
metadata = MetaData(naming_convention=convention)


@unique
class ShopUnitType(Enum):
    offer = 'OFFER'
    category = 'CATEGORY'


nodes_table = Table(
    'nodes',
    metadata,
    Column('id', String(36), primary_key=True),
    Column('name', String, nullable=False),
    Column('date', Date, nullable=False),
    Column('type', PgEnum(ShopUnitType, name="shop_unit_type"), nullable=False),
    Column('price', Integer)
)

nodes_children_table = Table(
    'nodes_children',
    metadata,
    Column('children_id', ForeignKey('nodes.id'), primary_key=True),
    Column('node_id', ForeignKey('nodes.id'))
)
