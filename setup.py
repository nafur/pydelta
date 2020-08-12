import setuptools

from pydelta import info

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name = info.PACKAGE_NAME,
    version = info.VERSION,
    description = info.DESCRIPTION,
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = info.REPOSITORY,
    author = info.AUTHOR,
    author_email = info.AUTHOR_EMAIL,
    license = 'MIT',
    packages = setuptools.find_packages(),
    zip_safe = False,
    scripts = [
        'bin/pydelta'
    ],
    install_requires = [
        'progressbar>=2.5',
        'sphinx-rtd-theme>=0.4.3',
        'importlib-metadata>=1.7 ; python_version<"3.8"',
    ]
)
