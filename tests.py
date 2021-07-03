#!/usr/bin/env pytest
from pathlib import Path
import asyncio

from asynctempfile import NamedTemporaryFile, \
  TemporaryDirectory
import pytest

from aiopath import AsyncPath


TEST_NAME: str = 'TEST'
TEST_SUFFIX: str = f'.{TEST_NAME}'


Paths = Path | AsyncPath | str


def get_paths(path: Paths) -> tuple[Path, AsyncPath]:
  return Path(path), AsyncPath(path)


def _test_is_pure(
  path: Path,
  apath: AsyncPath,
):
  # PurePath & AsyncPurePath methods are not async
  assert str(path) == str(apath)
  assert path.name == apath.name
  assert path.drive == apath.drive
  assert path.root == apath.root
  assert path.stem == apath.stem
  assert path.suffix == apath.suffix
  assert path.suffixes == apath.suffixes
  assert path.as_uri() == apath.as_uri()
  assert path.is_absolute() == apath.is_absolute()
  assert path.is_reserved() == apath.is_reserved()


async def _test_is_io(
  path: Path,
  apath: AsyncPath,
):
  # AsyncPath methods are async
  assert path.exists() == await apath.exists()
  assert path.is_dir() == await apath.is_dir()
  assert path.is_file() == await apath.is_file()
  assert path.is_fifo() == await apath.is_fifo()
  assert path.is_mount() == await apath.is_mount()
  assert path.is_socket() == await apath.is_socket()
  assert path.is_symlink() == await apath.is_symlink()
  assert path.is_char_device() == await apath.is_char_device()
  assert path.is_block_device() == await apath.is_block_device()


async def _test_is(
  path: Path,
  apath: AsyncPath,
  exists: bool = True,
  resolve: bool = False,
  test_parent: bool = True,
):
  _test_is_pure(path, apath)
  await _test_is_io(path, apath)

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
    aname, pname = str(apath), str(path)
    assert path.samefile(aname) and await apath.samefile(pname)

  if test_parent:
    await _test_is(
      path.parent,
      apath.parent,
      exists=exists,
      resolve=resolve,
      test_parent=False,
    )


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
  new_name: str = 'temp_dir_test'

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
async def test_write_read_text():
  text: str = 'example'

  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    await apath.write_text(text)
    result: str = await apath.read_text()
    assert result == text


@pytest.mark.asyncio
async def test_write_read_bytes():
  content: bytes = b'example'

  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    await apath.write_bytes(content)
    result: bytes = await apath.read_bytes()
    assert result == content


@pytest.mark.asyncio
async def test_touch():
  new_file: str = 'new_file'

  async with TemporaryDirectory() as temp:
    path, apath = get_paths(temp)
    file = path / new_file
    afile = apath / new_file

    assert not await afile.exists()
    await afile.touch()
    assert await afile.exists()


@pytest.mark.asyncio
async def test_stat():
  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    stat = await apath.stat()
    await apath.touch()
    new_stat = await apath.stat()

    assert not new_stat == stat


@pytest.mark.asyncio
async def test_glob():
  pass


@pytest.mark.asyncio
async def test_open():
  pass


@pytest.mark.asyncio
async def test_unlink():
  pass

