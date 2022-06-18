from datetime import datetime
from http import HTTPStatus

from aiohttp.web_response import Response

from comparer.api.handlers.base import BaseView
from comparer.db.schema import nodes_table, ShopUnitType, nodes_children_table


class ImportsView(BaseView):
    URL_PATH = '/imports'

    async def post(self):
        body = await self.request.json()
        updated_rows, insert_rows = await self.separate_existed_rows(body['items'], body['updateDate'])
        import_nodes_children = self.get_import_nodes_children(body['items'])

        async with self.pg.transaction() as conn:
            for node in insert_rows:
                query = nodes_table.insert().values(**node)
                query.parameters = {}
                await conn.fetchrow(query)

            for node in updated_rows:
                query = nodes_table.update(nodes_table.c.id == node['id']).values(**node)
                query.parameters = {}
                await conn.fetchrow(query)

            for node_id in import_nodes_children:
                for child_node_id in import_nodes_children[node_id]:
                    query = nodes_children_table.insert().values(node_id=node['id'], children_id=child_node_id)
                    query.parameters = {}
                    await conn.fetchrow(query)

        return Response(status=HTTPStatus.OK, text='Вставка или обновление прошли успешно')

    async def separate_existed_rows(self, import_nodes, import_date):
        updated_rows = []
        insert_rows = []
        for node in import_nodes:
            serialized_date = datetime.strptime(import_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            nodes_table_row = self.make_nodes_table_row(node, serialized_date)

            if await self.check_node_exists(node["id"]):
                updated_rows.append(nodes_table_row)
            else:
                insert_rows.append(nodes_table_row)
        return updated_rows, insert_rows

    @classmethod
    def make_nodes_table_row(cls, node, date):
        return {
            'id': node['id'],
            'name': node['name'],
            'date': date,
            'type': ShopUnitType(node['type']),
            'price': node['price']
        }

    @classmethod
    def get_import_nodes_children(cls, import_nodes):
        import_nodes_children = {}

        for node in import_nodes:
            if not import_nodes_children.get(node['parentId']):
                import_nodes_children[node['parentId']] = []
            import_nodes_children[node['parentId']].append(node['id'])

        return import_nodes_children