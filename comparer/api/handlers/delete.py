from uuid import UUID

from sqlalchemy import delete, or_

from comparer.api.handlers.base import BaseView
from comparer.db.schema import relates_table, nodes_table


class DeleteView(BaseView):
    URL_PATH = '/delete/{id}'

    async def delete(self):
        try:
            node_id = UUID(self.request.match_info['id'])
        except ValueError:
            return self.bad_request_response('Bad UUID')

        if not await self.check_node_exists(node_id):
            return self.not_found_response('Категория/товар не найден.')

        async with self.pg.transaction() as conn:
            deleted_nodes = await self.delete_node_children(conn, node_id)
            for deleted_node_id in deleted_nodes:
                query = delete(nodes_table).where(nodes_table.c.id == deleted_node_id)
                await conn.fetchrow(query)
        return self.ok_response('Удаление прошло успешно.')

    @classmethod
    async def delete_node_children(cls, conn, node_id):
        deleted_nodes = [node_id]

        query = delete(relates_table)\
            .where(or_(relates_table.c.node_id == node_id, relates_table.c.children_id == node_id))\
            .returning(relates_table.c.node_id, relates_table.c.children_id)
        for row in await conn.fetch(query):
            deleted_nodes += await cls.delete_node_children(conn, row['children_id'])

        return deleted_nodes
