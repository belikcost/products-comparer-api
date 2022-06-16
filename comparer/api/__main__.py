import logging

from aiohttp import web
from configargparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from aiomisc.log import basic_config

from comparer.utils.clear_env_vars import clear_env_vars
from comparer.utils.port_validator import positive_int

ENV_VARS_PREFIX = 'COMPARER_'

parser = ArgumentParser(
    auto_env_var_prefix=ENV_VARS_PREFIX,
    formatter_class=ArgumentDefaultsHelpFormatter
)

parser.add_argument('--api-address', default='0.0.0.0', help='IPv4/IPv6 address API server would listen on')
parser.add_argument('--api-port', type=positive_int, default=8080, help='TCP port API server would listen on')


def main():
    basic_config(logging.DEBUG, buffered=True)

    args = parser.parse_args()
    clear_env_vars(lambda arg_name: arg_name.startswith(ENV_VARS_PREFIX))

    app = web.Application()
    web.run_app(app, host=args.api_address, port=args.api_port)


if __name__ == '__main__':
    main()
