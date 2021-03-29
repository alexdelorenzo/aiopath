from __future__ import annotations
from typing import AsyncIterable, Union, Final, \
  TYPE_CHECKING, Optional, cast
from inspect import iscoroutinefunction
from pathlib import Path
import io

from aiofile import AIOFile, LineReader

if TYPE_CHECKING:  # keep mypy quiet
  from .path import AsyncPath


BEGINNING: Final[int] = 0
CHUNK_SIZE: Final[int] = 4 * 1_024

SEP: Final[str] = '\n'
ENCODING: Final[str] = 'utf-8'
ERRORS: Final[str] = 'replace'


Paths = Union['AsyncPath', Path, str]


class IterableAIOFile(AIOFile):
  def __init__(
    self,
    *args,
    errors: Optional[str] = ERRORS,
    newline: Optional[str] = SEP,
    **kwargs
  ):
    super().__init__(*args, **kwargs)
    self._errors: Optional[str] = errors
    self._newline: Optional[str] = newline

  def __aiter__(self) -> AsyncIterable[str]:
    newline: str = self._newline or SEP

    return read_lines(
      self.name,
      line_sep=newline
    )

  async def read_text(
    self,
    encoding: Optional[str] = None,
    errors: Optional[str] = None
  ) -> str:
    encoding = encoding or self.encoding or ENCODING
    errors = errors or self._errors or ERRORS

    return await read_full_file(
      self.name,
      encoding=encoding,
      errors=errors
    )


async def read_lines(
  path: Paths,
  line_sep: str = SEP,
  chunk_size: int = CHUNK_SIZE,
  offset: int = BEGINNING,
  encoding: str = ENCODING,
  errors: str = ERRORS,
  **kwargs
) -> AsyncIterable[str]: 
  if hasattr(path, 'resolve'):
    if iscoroutinefunction(path.resolve):
      path = str(await path.resolve())

    else:
      path = str(path.resolve())
  
  path: str = cast(str, path)

  async with AIOFile(path, 'rb') as handle:
    reader = LineReader(
      handle,
      line_sep=line_sep,
      chunk_size=chunk_size,
      offset=offset
    )

#    Python 3.8+
#    while line := await reader.readline()
#      yield line.decode(encoding, errors=errors)

    while True:
      line: bytes = await reader.readline()

      if not line:
        break

      yield line.decode(encoding, errors=errors)


async def read_full_file(
  path: Paths,
  line_sep: str = SEP,
  chunk_size: int = CHUNK_SIZE,
  offset: int = BEGINNING,
  encoding: str = ENCODING,
  errors: str = ERRORS,
  **kwargs
) -> str:
  lines_gen = read_lines(
    path,
    line_sep=line_sep,
    chunk_size=chunk_size,
    offset=offset,
    encoding=encoding,
    errors=errors
  )

  with io.StringIO() as string:
    async for line in lines_gen:
      string.write(line)

    return string.getvalue()
