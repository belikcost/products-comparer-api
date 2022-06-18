from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from sqlalchemy import select, exists

from comparer.db.schema import nodes_table


class BaseView(View):
    URL_PATH: str

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    async def check_node_exists(self, node_id):
        query = select([
            exists().where(nodes_table.c.id == node_id)
        ])

        return bool(await self.pg.fetchval(query))
