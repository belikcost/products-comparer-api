import logging
from functools import partial

from aiohttp import web
from configargparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from aiomisc.log import basic_config
from yarl import URL

from comparer.api.handlers import HANDLERS
from comparer.utils.clear_env_vars import clear_env_vars
from comparer.utils.pg import DEFAULT_PG_URL, setup_pg
from comparer.utils.port_validator import positive_int

ENV_VARS_PREFIX = 'COMPARER_'

log = logging.getLogger(__name__)

parser = ArgumentParser(
    auto_env_var_prefix=ENV_VARS_PREFIX,
    formatter_class=ArgumentDefaultsHelpFormatter
)

parser.add_argument('--api-address', default='0.0.0.0', help='IPv4/IPv6 address API server would listen on')
parser.add_argument('--api-port', type=positive_int, default=8080, help='TCP port API server would listen on')
parser.add_argument('--pg-url', type=URL, default=URL(DEFAULT_PG_URL), help='URL to use to connect to the database')
parser.add_argument('--pg-pool-min-size', type=int, default=10, help='Minimum database connections')
parser.add_argument('--pg-pool-max-size', type=int, default=10, help='Maximum database connections')


def main():
    basic_config(logging.DEBUG, buffered=True)

    args = parser.parse_args()
    clear_env_vars(lambda arg_name: arg_name.startswith(ENV_VARS_PREFIX))

    app = web.Application()
    app.cleanup_ctx.append(partial(setup_pg, args=args))

    for handler in HANDLERS:
        log.debug('Registering handler %r as %r', handler, handler.URL_PATH)
        app.router.add_route('*', handler.URL_PATH, handler)

    web.run_app(app, host=args.api_address, port=args.api_port)


if __name__ == '__main__':
    main()
