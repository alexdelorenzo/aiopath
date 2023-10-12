from __future__ import annotations
from pathlib import Path, PurePath
from asyncio import sleep, to_thread
from os import PathLike

from aiofiles.tempfile import NamedTemporaryFile, \
  TemporaryDirectory
from aiopath import AsyncPath, AsyncPurePath
import pytest

from . import file_paths, dir_paths, Paths, PathTypes, \
  get_paths, RECURSIVE_GLOB, WILDCARD_GLOB


NO_PATHS: int = 0


@pytest.mark.asyncio
async def test_readme_example1_basic():
  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    # check existence
    ## sync
    assert path.exists()
    ## async
    assert await apath.exists()

    # check if file
    ## sync
    assert path.is_file()
    ## async
    assert await apath.is_file()

    # touch
    path.touch()
    await apath.touch()

    # PurePath methods are not async
    assert path.is_absolute() == apath.is_absolute()
    assert path.as_uri() == apath.as_uri()

    # read and write text
    text: str = 'example'
    await apath.write_text(text)
    assert await apath.read_text() == text

  assert not path.exists()
  assert not await apath.exists()


@pytest.mark.asyncio
async def test_readme_example2_convert():
  home: Path = Path.home()
  ahome: AsyncPath = AsyncPath(home)
  path: Path = Path(ahome)

  assert isinstance(home, Path)
  assert isinstance(ahome, AsyncPath)
  assert isinstance(path, Path)

  # AsyncPath and Path objects can point to the same file
  assert str(home) == str(ahome) == str(path)

  # but AsyncPath and Path objects are equivalent
  assert home == ahome


@pytest.mark.asyncio
async def test_readme_example3_class_hierarchy():
  assert issubclass(AsyncPath, Path)
  assert issubclass(AsyncPath, PurePath)
  assert issubclass(AsyncPath, AsyncPurePath)
  assert issubclass(AsyncPurePath, PurePath)

  path: AsyncPath = await AsyncPath.home()

  assert isinstance(path, Path)
  assert isinstance(path, PurePath)
  assert isinstance(path, AsyncPurePath)


@pytest.mark.asyncio
async def test_readme_example4_read_write():
  text: str = 'example'

  async with NamedTemporaryFile() as temp:
    path = AsyncPath(temp.name)

    async with path.open(mode='w') as file:
      await file.write(text)

    async with path.open(mode='r') as file:
      result: str = await file.read()

    assert result == text

  async with NamedTemporaryFile() as temp:
    path = AsyncPath(temp.name)

    await path.write_text(text)
    result: str = await path.read_text()
    assert result == text

    content: bytes = text.encode()

    await path.write_bytes(content)
    result: bytes = await path.read_bytes()
    assert result == content


@pytest.mark.asyncio
async def test_readme_example5_glob():
  home: AsyncPath = await AsyncPath.home()

  async for path in home.glob(WILDCARD_GLOB):
    assert isinstance(path, AsyncPath)

  pkg_dir = AsyncPath(__file__).parent
  assert await pkg_dir.exists()

  paths = [path async for path in pkg_dir.glob(RECURSIVE_GLOB)]
  assert len(paths) > NO_PATHS
