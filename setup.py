__author__ = "Alex DeLorenzo"
from setuptools import setup
from pathlib import Path


PKG_NAME: str = "aiopath"
NAME: str = 'aiopath'
VERSION: str = "0.6.10"
LICENSE: str = "LGPL-3.0"

DESC: str = "📁 Async pathlib for Python"

REQUIREMENTS: list[str] = \
  Path('requirements.txt') \
    .read_text() \
    .splitlines()

README: str = Path('README.md').read_text()


setup(
  name=PKG_NAME,
  version=VERSION,
  description=DESC,
  long_description=README,
  long_description_content_type="text/markdown",
  url='https://github.com/alexdelorenzo/aiopath',
  author=__author__,
  license=LICENSE,
  packages=[NAME],
  zip_safe=True,
  install_requires=REQUIREMENTS,
  python_requires='>=3.10',
  include_package_data=True
)
