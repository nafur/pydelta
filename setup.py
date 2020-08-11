from setuptools import setup

from pydelta import info

setup(name='pydelta',
      version=info.__version__,
      description='Test',
      url=info.__repository__,
      author=info.__author__,
      author_email=info.__author_email__,
      license='MIT',
      packages=['pydelta'],
      zip_safe=False,
      scripts = [
          'bin/pydelta'
      ]
)