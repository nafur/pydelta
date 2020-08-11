from setuptools import setup

from pydelta import info

setup(
    name = info.PACKAGE_NAME,
    version = info.PYPI_VERSION,
    description = info.DESCRIPTION,
    url = info.REPOSITORY,
    author = info.AUTHOR,
    author_email = info.AUTHOR_EMAIL,
    license = 'MIT',
    packages = ['pydelta'],
    zip_safe = False,
    scripts = [
        'bin/pydelta'
    ]
)
