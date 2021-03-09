from __future__ import annotations
from typing import AsyncIterable, Union, List
from pathlib import Path
import io

from aiofile import AIOFile, LineReader


BEGINNING: int = 0
NO_SIZE: int = 0
CHUNK_SIZE: int = 1_096

SEP: str = '\n'
ENCODING: str = 'utf-8'
ERRORS: str = 'replace'


async def read_lines(
  path: Union[Path, str],
  line_sep: str = SEP,
  chunk_size: int = CHUNK_SIZE,
  offset: int = BEGINNING,
  encoding: str = ENCODING,
  errors: str = ERRORS,
  **kwargs
) -> AsyncIterable[str]:
  buffer = io.BytesIO()

  wrapper = io.TextIOWrapper(
    buffer,
    encoding=encoding,
    errors=errors,
  )

  if hasattr(path, 'resolve'):
    try:
      path = str(await path.resolve())

    except:
      path = str(path.resolve())

  async with AIOFile(path, 'rb') as handle:
    reader = LineReader(
      handle,
      line_sep=line_sep,
      chunk_size=chunk_size,
      offset=offset
    )

    while line := await reader.readline():
      buffer.write(line)
      buffer.seek(BEGINNING)

      yield wrapper.readline()


async def read_full_file(
  path: Union[Path, str],
  line_sep: str = SEP,
  chunk_size: int = CHUNK_SIZE,
  offset: int = BEGINNING,
  encoding: str = ENCODING,
  errors: str = ERRORS,
  **kwargs
) -> str:
  lines_gen = read_lines(
    path,
    line_sep,
    chunk_size,
    offset,
    encoding,
    errors
  )
  with io.StringIO() as string:
    async for line in lines_gen:
      string.write(line)

    return string.getvalue()
