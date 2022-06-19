import argparse
import logging
import os

from alembic.config import CommandLine
from alembic.config import Config

from pathlib import Path

from comparer.utils.pg import DEFAULT_PG_URL

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def make_alembic_config(cmd_opts, base_path: str = PROJECT_PATH) -> Config:
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location',
                               os.path.join(base_path, alembic_location))
    if cmd_opts.db_url:
        config.set_main_option('sqlalchemy.url', cmd_opts.db_url)

    return config


def main():
    logging.basicConfig(level=logging.DEBUG)

    alembic = CommandLine()
    alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    options = alembic.parser.parse_args()
    options.db_url = DEFAULT_PG_URL

    if 'cmd' not in options:
        alembic.parser.error('too few arguments')
        exit(128)
    else:
        config = make_alembic_config(options)
        exit(alembic.run_cmd(config, options))


if __name__ == '__main__':
    main()
