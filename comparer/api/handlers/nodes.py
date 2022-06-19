from uuid import UUID

from aiohttp.web_response import json_response
from sqlalchemy import select

from comparer.api.handlers.base import BaseView
from comparer.api.schema import GetNode
from comparer.db.schema import nodes_table, relates_table, ShopUnitType, imports_table


class NodesView(BaseView):
    URL_PATH = '/nodes/{id}'

    async def get(self):
        try:
            node_id = UUID(self.request.match_info['id'])
        except ValueError:
            return self.bad_request_response("Bad UUID")

        if not await self.check_node_exists(node_id):
            return self.not_found_response("Категория/товар не найден.")

        serialized_detail_node = await self.get_detail_node_with_children(node_id)
        return json_response(serialized_detail_node)

    async def get_detail_node_with_children(self, node_id):
        query = select(nodes_table).where(nodes_table.c.id == node_id)
        detail_node = dict(await self.pg.fetchrow(query))
        detail_node['type'] = ShopUnitType[detail_node['type']]

        if detail_node is None:
            return
        if detail_node['type'].value == ShopUnitType.offer.value:
            last_update = await self.get_node_update_date(node_id)
            return GetNode().dump({**detail_node, 'date': last_update, 'children': []})

        node_children = await self.get_node_children(node_id)
        detail_children = []

        for child_node_id in node_children:
            detail_child_node = await self.get_detail_node_with_children(child_node_id['id'])
            detail_children.append(detail_child_node)

        if len(node_children) == 0:
            detail_node['date'] = await self.get_node_update_date(node_id)

        detail_node['children'] = detail_children
        return GetNode().dump(detail_node)

    async def get_node_children(self, node_id):
        node_children = []
        query = select([relates_table.c.node_id, relates_table.c.children_id, imports_table.c.date]) \
            .where(relates_table.c.node_id == node_id) \
            .outerjoin(imports_table, imports_table.c.id == relates_table.c.import_id)

        for row in await self.pg.fetch(query):
            node_children.append({'id': row['children_id'], 'date': row['date']})
        return node_children

    async def get_node_update_date(self, node_id):
        query = select(imports_table.c.date) \
            .where(relates_table.c.children_id == node_id) \
            .outerjoin(imports_table, imports_table.c.id == relates_table.c.import_id)
        return await self.pg.fetchval(query)
