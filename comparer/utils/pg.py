import logging

from aiohttp.web_app import Application
from asyncpgsa import PG
from configargparse import Namespace

DEFAULT_PG_URL = "postgresql://db_user:db_password@db:5432/demo_db"

log = logging.getLogger(__name__)


async def setup_pg(app: Application, args: Namespace):
    log.info('Connecting to database: %s', args.pg_url)

    app['pg'] = PG()
    await app['pg'].init(
        str(args.pg_url),
        min_size=args.pg_pool_min_size,
        max_size=args.pg_pool_max_size
    )
    await app['pg'].fetchval('SELECT 1')
    log.info('Connected to database %s', args.pg_url)

    try:
        yield
    finally:
        log.info('Disconnecting from database %s', args.pg_url)
        await app['pg'].pool.close()
        log.info('Disconnected from database %s', args.pg_url)
