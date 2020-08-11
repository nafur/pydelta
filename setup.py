from setuptools import setup

from pydelta import info

setup(
    name = info.PROJECT_NAME,
    version=info.VERSION,
    description='Test',
    url=info.REPOSITORY,
    author=info.AUTHOR,
    author_email=info.AUTHOR_EMAIL,
    license='MIT',
    packages=['pydelta'],
    zip_safe=False,
    scripts = [
        'bin/pydelta'
    ]
)
