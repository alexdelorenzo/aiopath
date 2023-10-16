from __future__ import annotations

from inspect import getmembers, isasyncgenfunction, iscoroutinefunction, isfunction, isgeneratorfunction, ismethod, \
  ismethodwrapper, signature
from pathlib import Path
from typing import Any, Callable

import pytest
from aiofiles.tempfile import NamedTemporaryFile, TemporaryDirectory

from aiopath import AsyncPath
from aiopath.types import Paths as PathTypes
from aiopath.wrap import to_thread


WILDCARD_GLOB: str = '*'
RECURSIVE_GLOB: str = '**/*'

DUNDER: str = '__'
PRIVATE: str = '_'


type Paths = tuple[Path, AsyncPath]


def get_paths(path: PathTypes) -> Paths:
  return Path(path), AsyncPath(path)


def _is_method(obj: Any) -> bool:
  return (
    ismethod(obj)
    or isfunction(obj)
    or iscoroutinefunction(obj)
    or isasyncgenfunction(obj)
    or isgeneratorfunction(obj)
    or ismethodwrapper(obj)
  )


def _is_public_or_dunder(name: str) -> bool:
  return (
    name.startswith(DUNDER)
    and name.endswith(DUNDER)
    or not name.startswith(PRIVATE)
  )


def _get_public_methods(obj: Any) -> set[str]:
  return {
    name
    for name, _ in getmembers(obj, _is_method)
    if _is_public_or_dunder(name)
  }


def _get_signature_params(obj: Any, member: str) -> tuple[str, ...]:
  method: Callable = getattr(obj, member)
  sig = signature(method)
  params = sig.parameters.keys()

  return tuple(params)


@pytest.fixture
async def file_paths() -> Paths:
  async with NamedTemporaryFile() as temp:
    yield get_paths(temp.name)


@pytest.fixture
async def dir_paths() -> Paths:
  async with TemporaryDirectory() as temp:
    yield get_paths(temp)


def _test_is_pure(
  path: Path,
  apath: AsyncPath,
):
  # AsyncPurePath methods are not async
  assert str(path) == str(apath)
  assert path.anchor == apath.anchor
  assert path.name == apath.name
  assert path.drive == apath.drive
  assert path.parts == apath.parts
  assert path.root == apath.root
  assert path.stem == apath.stem
  assert path.suffix == apath.suffix
  assert path.suffixes == apath.suffixes
  assert path.as_uri() == apath.as_uri()
  assert path.as_posix() == apath.as_posix()
  assert path.is_absolute() == apath.is_absolute()
  assert path.is_reserved() == apath.is_reserved()
  assert path.is_relative_to(path) == apath.is_relative_to(apath)


async def _test_is_io(
  path: Path,
  apath: AsyncPath,
):
  # AsyncPath methods are async
  assert await to_thread(path.exists) == await apath.exists()
  assert await to_thread(path.is_dir) == await apath.is_dir()
  assert await to_thread(path.is_file) == await apath.is_file()
  assert await to_thread(path.is_fifo) == await apath.is_fifo()
  assert await to_thread(path.is_mount) == await apath.is_mount()
  assert await to_thread(path.is_socket) == await apath.is_socket()
  assert await to_thread(path.is_symlink) == await apath.is_symlink()
  assert await to_thread(path.is_char_device) == await apath.is_char_device()
  assert await to_thread(path.is_block_device) == await apath.is_block_device()


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
      await to_thread(path.resolve),
      await apath.resolve(),
      test_parent=False,
      resolve=False
    )

  if exists:
    assert await to_thread(path.lstat) == await apath.lstat()
    assert await to_thread(path.owner) == await apath.owner()
    assert await to_thread(path.group) == await apath.group()

    aname, pname = str(apath), str(path)
    assert await to_thread(path.samefile, aname) and await apath.samefile(pname)

  if test_parent:
    await _test_is(
      path.parent,
      apath.parent,
      exists=exists,
      resolve=resolve,
      test_parent=False,
    )
