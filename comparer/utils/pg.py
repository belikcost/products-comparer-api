import logging

from aiohttp.web_app import Application
from asyncpgsa import PG
from configargparse import Namespace

DEFAULT_PG_URL = "postgresql://db_user:db_password@localhost:5432/demo_db"
PASSWORD = "db_password"

log = logging.getLogger(__name__)


async def setup_pg(app: Application, args: Namespace):
    db_info = args.pg_url.with_password(PASSWORD)
    log.info('Connecting to database: %s', db_info)

    app['pg'] = PG()
    await app['pg'].init(
        str(args.pg_url),
        min_size=args.pg_pool_min_size,
        max_size=args.pg_pool_max_size
    )
    await app['pg'].fetchval('SELECT 1')
    log.info('Connected to database %s', db_info)

    try:
        yield
    finally:
        log.info('Disconnecting from database %s', db_info)
        await app['pg'].pool.close()
        log.info('Disconnected from database %s', db_info)
