from datetime import datetime
from http import HTTPStatus
from json import JSONDecodeError

from aiohttp.web_request import Request
from aiohttp.web_response import Response
from marshmallow import ValidationError
from sqlalchemy import select, exists

from comparer.api.handlers.base import BaseView
from comparer.api.schema import ImportNode, Import, UPDATE_DATE_FORMAT
from comparer.db.schema import nodes_table, ShopUnitType, nodes_children_table


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
            for node in self.body['items']:
                if str(node['id']) in existed_nodes_ids:
                    query = nodes_table.update(nodes_table.c.id == node['id']).values(**node,
                                                                                      date=self.body['updateDate'])
                else:
                    query = nodes_table.insert().values(**node, date=self.body['updateDate'])
                query.parameters = {}
                await conn.fetchrow(query)

            for node_id in import_nodes_children:
                for child_node_id in import_nodes_children[node_id]:
                    if await self.check_children_exist(child_node_id):
                        query = nodes_children_table.update(nodes_children_table.c.children_id == child_node_id).values(
                            node_id=node['id'], children_id=child_node_id)
                    else:
                        query = nodes_children_table.insert().values(node_id=node['id'], children_id=child_node_id)
                    query.parameters = {}
                    await conn.fetchrow(query)

        return Response(status=HTTPStatus.OK, text='Вставка или обновление прошли успешно')

    def deserialize_body(self):
        self.body = Import().load(self.body)
        self.body['items'] = [ImportNode().load(item) for item in self.body['items']]

    async def get_existed_nodes_ids(self):
        existed_nodes_ids = set()
        for node in self.body['items']:
            if await self.check_node_exists(node["id"]):
                existed_nodes_ids.add(str(node['id']))
        return existed_nodes_ids

    def get_import_nodes_children(self):
        import_nodes_children = {}

        for node in self.body['items']:
            if not import_nodes_children.get(node['parentId']):
                import_nodes_children[node['parentId']] = []
            import_nodes_children[node['parentId']].append(node['id'])
            node.pop('parentId')
        return import_nodes_children

    async def check_children_exist(self, children_id):
        query = select([
            exists().where(nodes_children_table.c.children_id == children_id)
        ])

        return bool(await self.pg.fetchval(query))
