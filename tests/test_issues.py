from __future__ import annotations
from pathlib import Path, PurePath
from asyncio import sleep, to_thread
from string import printable
from os import PathLike

from asynctempfile import NamedTemporaryFile, \
  TemporaryDirectory
import pytest

from aiopath import AsyncPath, AsyncPurePath

from . import _test_is, _test_is_io, _test_is_pure, \
  file_paths, dir_paths, Paths, PathTypes


# see https://github.com/alexdelorenzo/aiopath/issues/13
@pytest.mark.asyncio
async def test_issue_13(file_paths: Paths):
  _, apath = file_paths
  chunk_size: int = 10
  text = printable

  await apath.write_text(text)

  async with apath.open('r') as file:
    chunk = await file.read(chunk_size)
    assert chunk == text[:chunk_size]

    chunk = await file.read(chunk_size)
    next_slice = slice(chunk_size, chunk_size * 2)
    assert chunk == text[next_slice]

  data = text.encode()
  await apath.write_bytes(data)

  async with apath.open('rb') as file:
    chunk = await file.read(chunk_size)
    assert chunk == data[:chunk_size]

    chunk = await file.read(chunk_size)
    next_slice = slice(chunk_size, chunk_size * 2)
    assert chunk == data[next_slice]
