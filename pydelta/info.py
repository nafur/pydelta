import re
import subprocess

PACKAGE_NAME = 'pydelta-smt'
PROJECT_NAME = 'pyDelta'
DESCRIPTION = 'Delta debugger for SMT-LIB files'
VERSION = '0.1'
FULL_VERSION = subprocess.check_output(['git', 'describe', '--tags']).decode('utf8').strip()
PYPI_VERSION = re.sub('v([0-9.]+)-([0-9]+)-g[a-z0-9]+', '\\1.dev\\2', FULL_VERSION)
AUTHOR = 'Gereon Kremer'
AUTHOR_EMAIL  = 'gereon.kremer@gmail.com'
REPOSITORY = 'https://github.com/nafur/pydelta'
