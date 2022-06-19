import os
from importlib.machinery import SourceFileLoader

from pkg_resources import parse_requirements
from setuptools import find_packages, setup

module_name = 'comparer'

module = SourceFileLoader(
    module_name, os.path.join(module_name, '__init__.py')
).load_module()


def load_requirements(filename: str) -> list:
    requirements = []
    with open(filename, 'r') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


setup(
    name=module_name,
    version="1.0",
    platforms="all",
    packages=find_packages(exclude=["tests"]),
    install_requires=load_requirements("requirements.txt"),
    entry_points={
        "console_scripts":
            [
                "comparer-api = comparer.api.__main__:main",
                "comparer-db = comparer.db.__main__:main"
            ]
    },
    include_package_data=True,
)
