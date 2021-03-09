__author__ = "Alex DeLorenzo"
from setuptools import setup
from pathlib import Path


PKG_NAME = "aiopath"
NAME = 'aiopath'
VERSION = "0.3.0"
LICENSE = "LGPL-3.0"

DESC = "📁 Async pathlib for Python"

REQUIREMENTS = \
  Path('requirements.txt') \
    .read_text() \
    .splitlines()

README = Path('README.md').read_text()


setup(
  name=PKG_NAME,
  version=VERSION,
  description=DESC,
  long_description=README,
  long_description_content_type="text/markdown",
  url="https://alexdelorenzo.dev",
  author=__author__,
  license=LICENSE,
  packages=[NAME],
  zip_safe=False,
  install_requires=REQUIREMENTS,
  python_requires='>=3.7',
  include_package_data=True
)
