from __future__ import annotations

from string import printable

import pytest

from . import Paths, file_paths


# see https://github.com/alexdelorenzo/aiopath/issues/13
@pytest.mark.asyncio
async def test_issue_13_file_cursor(file_paths: Paths):
  _, apath = file_paths

  text: str = printable
  data: bytes = text.encode()

  chunk_size: int = 10
  first_slice = slice(chunk_size)
  next_slice = slice(chunk_size, chunk_size * 2)

  # test read/write text
  await apath.write_text(text)

  async with apath.open('r') as file:
    chunk = await file.read(chunk_size)
    assert chunk == text[first_slice]

    chunk = await file.read(chunk_size)
    assert chunk == text[next_slice]

  # test read/write bytes
  await apath.write_bytes(data)

  async with apath.open('rb') as file:
    chunk = await file.read(chunk_size)
    assert chunk == data[first_slice]

    chunk = await file.read(chunk_size)
    assert chunk == data[next_slice]
