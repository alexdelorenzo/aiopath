#!/usr/bin/env python3
from typing import Tuple, Union
from pathlib import Path
import asyncio

from asynctempfile import NamedTemporaryFile, \
  TemporaryDirectory
import pytest

from aiopath import AsyncPath


TEST_NAME: str = 'TEST'
TEST_SUFFIX: str = f'.{TEST_NAME}'


Paths = Union[Path, AsyncPath, str]


def get_paths(path: Paths) -> Tuple[Path, AsyncPath]:
  return Path(path), AsyncPath(path)


async def _test_is(
  path: Path,
  apath: AsyncPath,
  test_parent: bool = True,
  exists: bool = True,
  resolve: bool = True,
):
  # PurePath & AsyncPurePath methods are not async
  assert str(path) == str(apath)
  assert path.name == apath.name
  assert path.drive == apath.drive
  assert path.root == apath.root
  assert path.stem == apath.stem
  assert path.suffix == apath.suffix
  assert path.suffixes == apath.suffixes
  assert path.suffix == apath.suffix
  assert path.is_absolute() == apath.is_absolute()
  assert path.is_reserved() == apath.is_reserved()
  assert path.as_uri() == apath.as_uri()

  if test_parent:
    await _test_is(path.parent, apath.parent, test_parent=False)

  # AsyncPath methods are async
  assert path.exists() == await apath.exists()
  assert path.is_dir() == await apath.is_dir()
  assert path.is_file() == await apath.is_file()
  assert path.is_fifo() == await apath.is_fifo()
  assert path.is_block_device() == await apath.is_block_device()
  assert path.is_char_device() == await apath.is_char_device()
  assert path.is_mount() == await apath.is_mount()
  assert path.is_socket() == await apath.is_socket()
  assert path.is_symlink() == await apath.is_symlink()

  if exists and resolve:
    await _test_is(
      path.resolve(),
      await apath.resolve(),
      test_parent=False,
      resolve=False
    )

  if exists:
    assert path.lstat() == await apath.lstat()
    assert path.owner() == await apath.owner()
    assert path.group() == await apath.group()
    assert path.samefile(str(apath)) and await apath.samefile(path)


@pytest.mark.asyncio
async def test_home():
  home = Path.home()
  ahome = await AsyncPath.home()

  await _test_is(home, ahome)


@pytest.mark.asyncio
async def test_directory():
  async with TemporaryDirectory() as temp:
    path, apath = get_paths(temp)

    await _test_is(path, apath)
    await apath.touch()


@pytest.mark.asyncio
async def test_file():
  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    await _test_is(path, apath)
    await apath.touch()


@pytest.mark.asyncio
async def test_mkdir_rmdir():
  new_name = 'temp_dir_test'

  async with TemporaryDirectory() as temp:
    path, apath = get_paths(temp)
    new_apath = apath / new_name
    new_path = path / new_name

    await new_apath.mkdir()
    assert await new_apath.exists()
    await _test_is(new_path, new_apath)

    await new_apath.rmdir()
    assert not await new_apath.exists()
    assert not new_path.exists()
    await _test_is(new_path, new_apath, exists=False)


@pytest.mark.asyncio
async def test_name_suffix():
  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    await _test_is(
      path.with_suffix(TEST_SUFFIX),
      apath.with_suffix(TEST_SUFFIX),
      test_parent=False,
      exists=False
    )

    await _test_is(
      path.with_name(TEST_NAME),
      apath.with_name(TEST_NAME),
      test_parent=False,
      exists=False
    )


@pytest.mark.asyncio
async def test_symlink():
  pass


@pytest.mark.asyncio
async def test_write_text():
  pass


@pytest.mark.asyncio
async def test_write_bytes():
  pass


@pytest.mark.asyncio
async def test_read_text():
  pass


@pytest.mark.asyncio
async def test_read_bytes():
  pass


@pytest.mark.asyncio
async def test_touch():
  pass


@pytest.mark.asyncio
async def test_glob():
  pass

