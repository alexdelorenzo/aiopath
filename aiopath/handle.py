from __future__ import annotations
from typing import AsyncIterable, Union, \
  TYPE_CHECKING, Optional, cast, Tuple
from inspect import iscoroutinefunction
from contextlib import asynccontextmanager
from pathlib import Path
import io

from anyio import AsyncFile, open_file
from aiofile import AIOFile, LineReader

from .types import Final

if TYPE_CHECKING:  # keep mypy quiet
  from .path import AsyncPath


BEGINNING: Final[int] = 0
CHUNK_SIZE: Final[int] = 4 * 1_024

SEP: Final[str] = '\n'
ENCODING: Final[str] = 'utf-8'
ERRORS: Final[str] = 'replace'


Paths = Union['AsyncPath', Path, str]
FileData = Union[bytes, str]


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

    self._offset: int = 0

  def __aiter__(self) -> AsyncIterable[str]:
    encoding, errors, line_sep = self._get_options()

    return read_lines(
      self.name,
      line_sep,
      encoding=encoding,
      errors=errors,
    )

  def _set_offset(self, offset: int, data: FileData):
    self._offset = offset + len(data)

  def _get_options(
    self,
    encoding: Optional[str] = None,
    errors: Optional[str] = None
  ) -> Tuple[str, str, str]:
    encoding = encoding or self.encoding or ENCODING
    errors = errors or self._errors or ERRORS
    line_sep: str = self._newline or SEP

    return encoding, errors, line_sep

  async def read_text(
    self,
    encoding: Optional[str] = None,
    errors: Optional[str] = None
  ) -> str:
    encoding, errors, line_sep = self._get_options(encoding, errors)

    return await read_full_file(
      self.name,
      line_sep,
      encoding=encoding,
      errors=errors
    )

  async def read(
    self,
    size: int = -1,
    offset: Optional[int] = None
  ) -> FileData:
    if offset is None:
      offset = self._offset

    data: FileData = await super().read(size, offset)
    self._set_offset(offset, data)

    return data

  async def write(
    self,
    data: FileData,
    offset: Optional[int] = None
  ):
    if offset is None:
      offset = self._offset

    await super().write(data, offset)
    self._set_offset(offset, data)


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

  path = cast(str, path)

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


Handle = AsyncFile


@asynccontextmanager
async def get_handle(
  name: str,
  mode: FileMode = 'r',
  buffering: int = -1,
  encoding: str | None = ENCODING,
  errors: str | None = ERRORS,
  newline: str | None = SEP,
) -> AsyncContextManager[Handle]:
  file: AsyncFile

  if 'b' in mode:
    file = await open_file(name, mode)

  else:
    file = await open_file(
      name,
      mode,
      encoding=encoding,
      errors=errors,
      newline=newline,
    )

  yield file
  await file.aclose()
