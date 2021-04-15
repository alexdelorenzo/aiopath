#!/usr/bin/env python3
from typing import Tuple, Union
from pathlib import Path
import asyncio

from asynctempfile import NamedTemporaryFile, \
  TemporaryDirectory
import pytest

from aiopath import AsyncPath


Paths = Union[Path, AsyncPath, str]


def get_paths(path: Paths) -> Tuple[Path, AsyncPath]:
  return Path(path), AsyncPath(path)


@pytest.mark.asyncio
async def test_home():
  home = Path.home()
  ahome = await AsyncPath.home()

  assert str(home) == str(ahome)
  assert home.exists() == await ahome.exists()


@pytest.mark.asyncio
async def test_directory():
  async with TemporaryDirectory() as temp:
    path, apath = get_paths(temp)

    assert path.exists() == await apath.exists()
    assert path.is_dir() == await apath.is_dir()
    assert path.is_file() == await apath.is_file()
    assert path.is_fifo() == await apath.is_fifo()


@pytest.mark.asyncio
async def test_file():
  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    assert path.exists() == await apath.exists()
    assert path.is_dir() == await apath.is_dir()
    assert path.is_file() == await apath.is_file()
    assert path.is_fifo() == await apath.is_fifo()


@pytest.mark.asyncio
async def test_mkdir_rmdir():
  new_name = 'temp_dir_test'

  async with TemporaryDirectory() as temp:
    path, apath = get_paths(temp)
    new_apath = apath / new_name
    new_path = path / new_name

    await new_apath.mkdir()
    assert await new_apath.exists()
    await new_apath.rmdir()
    assert not await new_apath.exists()
    assert not new_path.exists()
