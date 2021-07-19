from __future__ import annotations
from pathlib import Path, PurePath
from asyncio import sleep, to_thread
from os import PathLike

from asynctempfile import NamedTemporaryFile, \
  TemporaryDirectory
import pytest

from aiopath import AsyncPath, AsyncPurePath

from . import _test_is, _test_is_io, _test_is_pure, \
  file_paths, dir_paths, Paths, PathTypes


TEST_NAME: str = 'TEST'
TEST_SUFFIX: str = f'.{TEST_NAME}'
TOUCH_SLEEP: int = 1


@pytest.mark.asyncio
async def test_home():
  home = Path.home()
  ahome = await AsyncPath.home()

  await _test_is(home, ahome)


@pytest.mark.asyncio
async def test_directory(dir_paths: Paths):
  await _test_is(*dir_paths)


@pytest.mark.asyncio
async def test_file(file_paths: Paths):
  await _test_is(*file_paths)


@pytest.mark.asyncio
async def test_mkdir_rmdir(dir_paths: Paths):
  path, apath = dir_paths

  new_name: str = 'temp_dir_test'
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
async def test_with_name_with_suffix(file_paths: Paths):
  path, apath = file_paths

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
async def test_write_read_text(file_paths: Paths):
  path, apath = file_paths

  text: str = 'example'
  await apath.write_text(text)
  result: str = await apath.read_text()

  assert result == text


@pytest.mark.asyncio
async def test_write_read_bytes(file_paths: Paths):
  path, apath = file_paths

  content: bytes = b'example'
  await apath.write_bytes(content)
  result: bytes = await apath.read_bytes()

  assert result == content


@pytest.mark.asyncio
async def test_touch(dir_paths: Paths):
  path, apath = dir_paths
  file = path / TEST_NAME
  afile = apath / TEST_NAME

  assert not await afile.exists()
  await afile.touch()
  assert await afile.exists()


@pytest.mark.asyncio
async def test_stat(file_paths: Paths):
  path, apath = file_paths
  stat = await apath.stat()

  await sleep(TOUCH_SLEEP)
  await apath.touch()

  new_stat = await apath.stat()

  # stat.st_ctime should be different
  assert not new_stat == stat


@pytest.mark.asyncio
async def test_unlink(file_paths: Paths, dir_paths: Paths):
  path, apath = file_paths

  assert await apath.exists()
  assert path.exists()

  await apath.unlink()
  assert not await apath.exists()
  assert not path.exists()

  # recreate file
  await apath.touch()

  path, apath = dir_paths

  # can't unlink dirs
  with pytest.raises(IsADirectoryError):
    await apath.unlink()

  assert await apath.exists()
  assert path.exists()


@pytest.mark.asyncio
async def test_links():
  # symlink
  ## readlink()
  ## symlink_to()

  # hard link
  ## link_to()
  pass


@pytest.mark.asyncio
async def test_rglob():
  pass


@pytest.mark.asyncio
async def test_open():
  pass


@pytest.mark.asyncio
async def test_chmod():
  pass


@pytest.mark.asyncio
async def test_rename():
  pass


@pytest.mark.asyncio
async def test_replace():
  pass


@pytest.mark.asyncio
async def test_cwd():
  pass


@pytest.mark.asyncio
async def test_samefile():
  pass


@pytest.mark.asyncio
async def test_iterdir():
  pass


@pytest.mark.asyncio
async def test_absolute():
  pass


@pytest.mark.asyncio
async def test_resolve():
  pass


@pytest.mark.asyncio
async def test_lstat():
  pass


@pytest.mark.asyncio
async def test_owner():
  pass


@pytest.mark.asyncio
async def test_group():
  pass


@pytest.mark.asyncio
async def test_is_mount():
  pass


@pytest.mark.asyncio
async def test_expand_user():
  pass
