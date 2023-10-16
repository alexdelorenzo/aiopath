from __future__ import annotations

from functools import cached_property
from os import stat_result
from pathlib import Path, PurePath
from typing import AsyncContextManager, AsyncIterable, Self

from .handle import Handle, get_handle
from .metadata import docs_from
from .types import FileMode, Paths
from .wrap import to_thread


class AsyncPurePath(PurePath):
  """
  An implementation of pathlib.PurePath that returns asynchronous Path objects.

  Instead of returning PurePath objects, AsyncPurePath returns AsyncPath objects.
  """

  __slots__ = PurePath.__slots__

  @docs_from(PurePath)
  def __rtruediv__(self, key: Paths) -> Self:
    path: PurePath = super().__rtruediv__(key)
    return AsyncPath(path)

  @docs_from(PurePath)
  def __truediv__(self, key: Paths) -> Self:
    path: PurePath = super().__truediv__(key)
    return AsyncPath(path)

  @property
  @docs_from(PurePath)
  def parent(self: Self) -> Self:
    path: PurePath = super().parent
    return AsyncPath(path)

  @property
  @docs_from(PurePath)
  def parents(self: Self) -> tuple[Self, ...]:
    return tuple(AsyncPath(path) for path in super().parents)

  @docs_from(PurePath)
  def joinpath(self: Self, *pathsegments: str) -> Self:
    path: PurePath = super().joinpath(*pathsegments)
    return AsyncPath(path)

  @docs_from(PurePath)
  def relative_to(self, other: Paths, /, *_deprecated, walk_up: bool = False) -> Self:
    path: PurePath = super().relative_to(other, *_deprecated, walk_up=walk_up)
    return AsyncPath(path)

  @docs_from(PurePath)
  def with_name(self: Self, name: str) -> Self:
    path: PurePath = super().with_name(name)
    return AsyncPath(path)

  @docs_from(PurePath)
  def with_suffix(self: Self, suffix: str) -> Self:
    path: PurePath = super().with_suffix(suffix)
    return AsyncPath(path)


class AsyncPath(AsyncPurePath, Path):
  """An asynchronous implementation of pathlib.Path."""

  __slots__ = (
    *Path.__slots__,
    '__dict__',  # required for functools.cached_property()
  )

  @cached_property
  def _path(self) -> Path:
    return Path(self)

  @classmethod
  @docs_from(Path)
  async def cwd(cls) -> Self:
    path: Path = await to_thread(Path.cwd)
    return AsyncPath(path)

  @classmethod
  @docs_from(Path)
  async def home(cls) -> Self:
    path: Path = await to_thread(Path.home)
    return AsyncPath(path)

  @docs_from(Path)
  async def absolute(self: Self) -> Self:
    path: Path = await to_thread(super().absolute)
    return AsyncPath(path)

  @docs_from(Path)
  async def chmod(self, mode: FileMode, *, follow_symlinks: bool = True):
    return await to_thread(super().chmod, mode, follow_symlinks=follow_symlinks)

  @docs_from(Path)
  async def exists(self, *, follow_symlinks: bool = True) -> bool:
    return await to_thread(self._path.exists, follow_symlinks=follow_symlinks)

  @docs_from(Path)
  async def expanduser(self: Self) -> Self:
    path: Path = await to_thread(super().expanduser)
    return AsyncPath(path)

  @docs_from(Path)
  async def glob(self: Self, pattern: str, *, case_sensitive: bool | None = None) -> AsyncIterable[Self]:
    for path in await to_thread(self._path.glob, pattern, case_sensitive=case_sensitive):
      yield AsyncPath(path)

  @docs_from(Path)
  async def group(self) -> str:
    return await to_thread(self._path.group)

  @docs_from(Path)
  async def hardlink_to(
    self,
    target: Paths,
  ):
    return await to_thread(super().hardlink_to, target)

  @docs_from(Path)
  async def is_block_device(self) -> bool:
    return await to_thread(self._path.is_block_device)

  @docs_from(Path)
  async def is_char_device(self) -> bool:
    return await to_thread(self._path.is_char_device)

  @docs_from(Path)
  async def is_dir(self) -> bool:
    return await to_thread(self._path.is_dir)

  @docs_from(Path)
  async def is_fifo(self) -> bool:
    return await to_thread(self._path.is_fifo)

  @docs_from(Path)
  async def is_file(self) -> bool:
    return await to_thread(self._path.is_file)

  @docs_from(Path)
  async def is_mount(self) -> bool:
    return await to_thread(self._path.is_mount)

  @docs_from(Path)
  async def is_socket(self) -> bool:
    return await to_thread(self._path.is_socket)

  @docs_from(Path)
  async def is_symlink(self) -> bool:
    return await to_thread(self._path.is_symlink)

  @docs_from(Path)
  async def iterdir(self: Self) -> AsyncIterable[Self]:
    for path in await to_thread(super().iterdir):
      yield AsyncPath(path)

  @docs_from(Path)
  async def lchmod(self, mode: FileMode):
    return await to_thread(self._path.lchmod, mode)

  @docs_from(Path)
  async def lstat(self) -> stat_result:
    return await to_thread(self._path.lstat)

  @docs_from(Path)
  async def match(self, path_pattern: str, *, case_sensitive: bool | None = None) -> bool:
    return await to_thread(super().match, path_pattern, case_sensitive=case_sensitive)

  @docs_from(Path)
  async def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False):
    return await to_thread(self._path.mkdir, mode, parents, exist_ok)

  @docs_from(Path)
  def open(
    self,
    mode: str = FileMode,
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
  ) -> AsyncContextManager[Handle]:
    return get_handle(str(self), mode, buffering, encoding, errors, newline)

  @docs_from(Path)
  async def owner(self) -> str:
    return await to_thread(self._path.owner)

  @docs_from(Path)
  async def read_bytes(self) -> bytes:
    return await to_thread(self._path.read_bytes)

  @docs_from(Path)
  async def read_text(self, encoding: str | None = None, errors: str | None = None) -> str:
    return await to_thread(self._path.read_text, encoding, errors)

  @docs_from(Path)
  async def readlink(self: Self) -> Self:
    path: Path = await to_thread(super().readlink)
    return AsyncPath(path)

  @docs_from(Path)
  async def rename(self: Self, target: Paths) -> Self:
    path: Path = await to_thread(super().rename, target)
    return AsyncPath(path)

  @docs_from(Path)
  async def replace(self: Self, target: Paths) -> Self:
    path: Path = await to_thread(super().replace, target)
    return AsyncPath(path)

  @docs_from(Path)
  async def resolve(self: Self, strict: bool = False) -> Self:
    path: Path = await to_thread(super().resolve, strict)
    return AsyncPath(path)

  @docs_from(Path)
  async def rglob(self: Self, pattern: str, *, case_sensitive: bool | None = None) -> AsyncIterable[Self]:
    for path in await to_thread(super().rglob, pattern, case_sensitive=case_sensitive):
      yield AsyncPath(path)

  @docs_from(Path)
  async def rmdir(self):
    return await to_thread(super().rmdir)

  @docs_from(Path)
  async def samefile(self, other_path: Paths) -> bool:
    return await to_thread(self._path.samefile, other_path)

  @docs_from(Path)
  async def stat(self, *, follow_symlinks: bool = True) -> stat_result:
    return await to_thread(super().stat, follow_symlinks=follow_symlinks)

  @docs_from(Path)
  async def symlink_to(self, target: Paths, target_is_directory: bool = False):
    return await to_thread(super().symlink_to, target, target_is_directory)

  @docs_from(Path)
  async def touch(self, mode: int = 0o666, exist_ok: bool = True):
    return await to_thread(super().touch, mode, exist_ok)

  @docs_from(Path)
  async def unlink(self, missing_ok: bool = False):
    return await to_thread(super().unlink, missing_ok)

  @docs_from(Path)
  async def write_bytes(self, data: bytes) -> int:
    return await to_thread(self._path.write_bytes, data)

  @docs_from(Path)
  async def write_text(
    self,
    data: str,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None
  ) -> int:
    return await to_thread(self._path.write_text, data, encoding, errors, newline)
