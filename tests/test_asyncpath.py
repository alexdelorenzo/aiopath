from __future__ import annotations

from asyncio import sleep
from inspect import getmembers, ismethod, signature
from pathlib import Path
from typing import Any, Callable

import pytest

from aiopath import AsyncPath
from . import Paths, _test_is, dir_paths, file_paths


TEST_NAME: str = 'TEST'
TEST_SUFFIX: str = f'.{TEST_NAME}'
TOUCH_SLEEP: int = 1

DUNDER: str = '__'
PRIVATE: str = '_'


def _get_signature_params(obj: Any, member: str) -> set[str]:
  method: Callable = getattr(obj, member)
  sig = signature(method)
  params = sig.parameters.keys()

  return set(params)


def test_asyncpath_implements_all_path_members():
  path_dunders: set[str] = {
    member
    for member in dir(Path)
    if member.startswith(DUNDER) and member.endswith(DUNDER)
  }
  path_public: set[str] = {
    member
    for member in dir(Path)
    if not member.startswith(PRIVATE)
  }
  path_members: set[str] = path_dunders | path_public

  apath_dunders: set[str] = {
    member
    for member in dir(AsyncPath)
    if member.startswith(DUNDER) and member.endswith(DUNDER)
  }
  apath_public: set[str] = {
    member
    for member in dir(AsyncPath)
    if not member.startswith(PRIVATE)
  }
  apath_members: set[str] = apath_dunders | apath_public

  assert apath_members >= path_members


def test_asyncpath_method_signatures_match_path_method_signatures():
  amethods: set[str] = {name for name, _ in getmembers(AsyncPath, ismethod)}
  methods: set[str] = {name for name, _ in getmembers(Path, ismethod)}

  asigs: dict[str, set[str]] = {
    method: _get_signature_params(AsyncPath, method)
    for method in amethods
  }
  sigs: dict[str, set[str]] = {
    method: _get_signature_params(Path, method)
    for method in methods
  }

  assert asigs == sigs


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
async def test_links(file_paths: Paths):
  # symlink
  ## readlink()
  ## symlink_to()

  # hard link
  ## link_to()
  pass


@pytest.mark.asyncio
async def test_rglob(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_open(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_chmod(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_rename(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_replace(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_cwd(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_samefile(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_iterdir(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_absolute(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_resolve(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_lstat(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_owner(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_group(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_is_mount(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_expanduser(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_match(file_paths: Paths):
  pass


@pytest.mark.asyncio
async def test_joinpath(file_paths: Paths):
  pass
