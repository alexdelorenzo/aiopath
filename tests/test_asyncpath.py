from __future__ import annotations

from asyncio import sleep
from inspect import getdoc
from pathlib import Path, PurePath

import pytest

from aiopath import AsyncPath, AsyncPurePath
from aiopath.wrap import to_thread
from . import Paths, _get_public_methods, _get_signature_params, \
  _is_public_or_dunder, _test_is, file_paths, dir_paths


TEST_NAME: str = 'TEST'
TEST_SUFFIX: str = f'.{TEST_NAME}'
TOUCH_SLEEP: int = 1

ASYNCPUREPATH_MRO: list[type] = [
  AsyncPurePath,
  PurePath,
  object,
]
ASYNCPATH_MRO: list[type] = [
  AsyncPath,
  AsyncPurePath,
  Path,
  PurePath,
  object,
]


def test_mro():
  assert AsyncPurePath.mro() == ASYNCPUREPATH_MRO
  assert AsyncPath.mro() == ASYNCPATH_MRO


def test_asyncpath_implements_all_path_members():
  path_members: set[str] = {
    member
    for member in dir(Path)
    if _is_public_or_dunder(member)
  }

  apath_members: set[str] = {
    member
    for member in dir(AsyncPath)
    if _is_public_or_dunder(member)
  }

  assert apath_members >= path_members


def test_asyncpath_method_signatures_match_path_method_signatures():
  amethods = _get_public_methods(AsyncPath)
  pmethods = _get_public_methods(Path)

  methods = amethods & pmethods

  asigs: dict[str, tuple[str, ...]] = {
    method: _get_signature_params(AsyncPath, method)
    for method in methods
  }

  psigs: dict[str, tuple[str, ...]] = {
    method: _get_signature_params(Path, method)
    for method in methods
  }

  assert asigs == psigs


def test_asyncpath_methods_inherit_docs_from_path_methods():
  amethods = _get_public_methods(AsyncPath)
  pmethods = _get_public_methods(Path)

  methods = amethods & pmethods

  for method in methods:
    amethod = getattr(AsyncPath, method)
    pmethod = getattr(Path, method)

    assert getdoc(amethod) == getdoc(pmethod)


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
async def test_with_name(file_paths: Paths):
  path, apath = file_paths

  await _test_is(
    path.with_suffix(TEST_SUFFIX),
    apath.with_suffix(TEST_SUFFIX),
    test_parent=False,
    exists=False
  )


@pytest.mark.asyncio
async def test_with_suffix(file_paths: Paths):
  path, apath = file_paths

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
  assert await to_thread(path.exists)

  await apath.unlink()
  assert not await apath.exists()
  assert not await to_thread(path.exists)

  # recreate file
  await apath.touch()

  path, apath = dir_paths

  # can't unlink dirs
  with pytest.raises(IsADirectoryError):
    await apath.unlink()

  assert await apath.exists()
  assert await to_thread(path.exists)


@pytest.mark.asyncio
async def test_symlinks(file_paths: Paths, dir_paths: Paths):
  path, apath = file_paths
  pdir, adir = dir_paths
  new_apath = apath.parent / 'symlink'

  for _path in (apath, adir):
    is_dir: bool = await _path.is_dir()

    await new_apath.symlink_to(_path, target_is_directory=is_dir)
    assert await new_apath.exists()
    assert await new_apath.is_symlink()

    link = await new_apath.readlink()
    assert link == _path

    assert await link.is_dir() == is_dir
    assert await link.is_file() != is_dir

    await new_apath.unlink()
    assert not await new_apath.exists()


@pytest.mark.asyncio
async def test_hardlinks(file_paths: Paths, dir_paths: Paths):
  apath = AsyncPath(__file__)
  adir = apath.parent
  new_apath = apath.parent / 'hardlink'

  for _path in (apath, adir):
    await new_apath.hardlink_to(apath)
    assert await new_apath.exists()
    assert not await new_apath.is_symlink()

    with pytest.raises(OSError):
      await new_apath.readlink()

    await new_apath.unlink()
    assert not await new_apath.exists()


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
