from enum import unique, Enum

from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, DateTime, BIGINT
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum

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


imports_table = Table(
    'imports',
    metadata,
    Column('id', BIGINT, primary_key=True, autoincrement=True),
    Column('date', DateTime, nullable=False),
)

nodes_table = Table(
    'nodes',
    metadata,
    Column('id', UUID, primary_key=True),
    Column('name', String, nullable=False),
    Column('type', PGEnum(ShopUnitType), nullable=False),
    Column('price', Integer),
    Column('parent_id', UUID)
)

relates_table = Table(
    'relates',
    metadata,
    Column('children_id', ForeignKey('nodes.id'), primary_key=True),
    Column('node_id', UUID),
    Column('import_id', ForeignKey('imports.id'), nullable=False)
)
