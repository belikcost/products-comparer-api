from json import JSONDecodeError

from aiohttp.web_request import Request
from marshmallow import ValidationError
from sqlalchemy import select, exists

from comparer.api.handlers.base import BaseView
from comparer.api.schema import Import
from comparer.db.schema import nodes_table, relates_table, imports_table


class ImportsView(BaseView):
    URL_PATH = '/imports'

    def __init__(self, request: Request):
        super().__init__(request)
        self.body = None

    async def post(self):
        try:
            self.body = await self.request.json()
        except JSONDecodeError:
            return self.bad_request_response('Invalid JSON')
        try:
            self.deserialize_body()
        except ValidationError as err:
            return self.bad_request_response(err.messages)

        existed_nodes_ids = await self.get_existed_nodes_ids()
        import_nodes_children = self.get_import_nodes_children()

        async with self.pg.transaction() as conn:
            query = imports_table.insert().values(date=self.body['update_date']).returning(imports_table.c.id)
            query.parameters = {}
            import_id = await conn.fetchval(query)

            for node in self.body['items']:
                if str(node['id']) in existed_nodes_ids:
                    query = nodes_table.update(nodes_table.c.id == node['id']).values(**node)
                else:
                    query = nodes_table.insert().values(**node)
                query.parameters = {}
                await conn.fetchrow(query)

                if node['id'] not in import_nodes_children:
                    if await self.check_children_exist(conn, node['id']):
                        query = relates_table.update(relates_table.c.children_id == node['id']).values(
                            children_id=node['id'], import_id=import_id
                        )
                    else:
                        query = relates_table.insert().values(
                            children_id=node['id'], import_id=import_id
                        )
                    query.parameters = {}
                    await conn.fetchrow(query)

            for node_id in import_nodes_children:
                for child_node_id in import_nodes_children[node_id]:
                    if await self.check_children_exist(conn, child_node_id):
                        query = relates_table.update(relates_table.c.children_id == child_node_id).values(
                            node_id=node_id, children_id=child_node_id, import_id=import_id
                        )
                    else:
                        query = relates_table.insert().values(
                            children_id=child_node_id, node_id=node_id, import_id=import_id
                        )
                    query.parameters = {}
                    await conn.fetchrow(query)

        return self.ok_response('Вставка или обновление прошли успешно')

    def deserialize_body(self):
        self.body = Import().load(self.body)

    async def get_existed_nodes_ids(self):
        existed_nodes_ids = set()
        for node in self.body['items']:
            if await self.check_node_exists(node["id"]):
                existed_nodes_ids.add(str(node['id']))
        return existed_nodes_ids

    def get_import_nodes_children(self):
        import_nodes_children = {}

        for node in self.body['items']:
            if node['parent_id'] is None:
                continue
            if not import_nodes_children.get(node['parent_id']):
                import_nodes_children[node['parent_id']] = []
            import_nodes_children[node['parent_id']].append(node['id'])
        return import_nodes_children

    @classmethod
    async def check_children_exist(cls, conn, children_id):
        query = select([
            exists().where(relates_table.c.children_id == children_id)
        ])

        return bool(await conn.fetchval(query))
