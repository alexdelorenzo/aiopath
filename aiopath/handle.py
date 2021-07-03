from __future__ import annotations
from typing import AsyncIterable, Union, IO, \
  TYPE_CHECKING, cast, Final, TextIO, BinaryIO, \
  AsyncContextManager
from inspect import iscoroutinefunction
from contextlib import asynccontextmanager
from pathlib import Path
import io

from aiofile import AIOFile, LineReader, \
  TextFileWrapper, BinaryFileWrapper
from anyio import AsyncFile, open_file

from .types import FileMode

if TYPE_CHECKING:  # keep mypy quiet
  from .path import AsyncPath


BEGINNING: Final[int] = 0
CHUNK_SIZE: Final[int] = 4 * 1_024

SEP: Final[str] = '\n'
ENCODING: Final[str] = 'utf-8'
ERRORS: Final[str] = 'replace'


Paths = Union['AsyncPath', Path, str]
FileData = bytes | str


class FileLike(IO):
  is_binary: bool


class TextFile(FileLike, TextIO):
  pass


class BinaryFile(FileLike, BinaryIO):
  pass


class IterableAIOFile(FileLike, AIOFile):
  def __init__(
    self,
    *args,
    errors: str | None = ERRORS,
    newline: str | None = SEP,
    **kwargs
  ):
    super().__init__(*args, **kwargs)
    self._errors: str | None = errors
    self._newline: str | None = newline

    self._offset: int = 0
    self._mode: str = self.__open_mode

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
    encoding: str | None = None,
    errors: str | None = None
  ) -> tuple[str, str, str]:
    encoding = encoding or self.encoding or ENCODING
    errors = errors or self._errors or ERRORS
    line_sep: str = self._newline or SEP

    return encoding, errors, line_sep

  async def read_text(
    self,
    encoding: str | None = None,
    errors: str | None = None
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
    offset: int | None = None
  ) -> FileData:
    if offset is None:
      offset = self._offset

    data: FileData = await super().read(size, offset)
    self._set_offset(offset, data)

    return data

  async def write(
    self,
    data: FileData,
    offset: int | None = None
  ):
    if offset is None:
      offset = self._offset

    await super().write(data, offset)
    self._set_offset(offset, data)


Handle = \
  TextFileWrapper | BinaryFileWrapper | IterableAIOFile | AsyncFile


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

    while line := await reader.readline():
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
