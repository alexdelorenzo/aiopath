from functools import cached_property
from os import stat_result
from pathlib import Path, PurePath
from typing import AsyncIterable, Self

from .old.handle import get_handle
from .types import FileMode
from .wrap import to_thread


class AsyncPurePath(PurePath):
  __slots__ = PurePath.__slots__

  def __truediv__(self, other: Self) -> Self:
    path: PurePath = super().__truediv__(other)
    return AsyncPath(path)

  def __rtruediv__(self, other: Self) -> Self:
    path: PurePath = super().__rtruediv__(other)
    return AsyncPath(path)

  def relative_to(self: Self, *other: str | Path) -> Self:
    path: PurePath = super().relative_to(*other)
    return AsyncPath(path)

  def with_name(self: Self, name: str) -> Self:
    path: PurePath = super().with_name(name)
    return AsyncPath(path)

  def with_suffix(self: Self, suffix: str) -> Self:
    path: PurePath = super().with_suffix(suffix)
    return AsyncPath(path)

  def joinpath(self: Self, *other: str | Path) -> Self:
    path: PurePath = super().joinpath(*other)
    return AsyncPath(path)

  @property
  def parent(self: Self) -> Self:
    path: PurePath = super().parent
    return AsyncPath(path)

  @property
  def parents(self: Self) -> tuple[Self, ...]:
    return tuple(AsyncPath(path) for path in super().parents)


class AsyncPath(Path, AsyncPurePath):
  __slots__ = ('__dict__',)

  @cached_property
  def _path(self) -> Path:
    return Path(self)

  def open(
    self,
    mode: str = FileMode,
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
  ) -> Self:
    return get_handle(
      str(self),
      mode,
      buffering,
      encoding,
      errors,
      newline
    )

  @classmethod
  async def cwd(cls) -> Self:
    path: Path = await to_thread(Path.cwd)
    return AsyncPath(path)

  @classmethod
  async def home(cls) -> Self:
    path: Path = await to_thread(Path.home)
    return AsyncPath(path)

  async def stat(self) -> stat_result:
    return await to_thread(super().stat)

  async def chmod(
    self,
    mode: int | str,
    *,
    follow_symlinks: bool = True,
  ):
    return await to_thread(super().chmod, mode, follow_symlinks=follow_symlinks)

  async def lchmod(
    self,
    mode: int | str,
  ):
    return await to_thread(super().lchmod, mode)

  async def absolute(self: Self) -> Self:
    path: Path = await to_thread(super().absolute)
    return AsyncPath(path)

  async def exists(self) -> bool:
    return await to_thread(self._path.exists)

  async def expanduser(self: Self) -> Self:
    path: Path = await to_thread(super().expanduser)
    return AsyncPath(path)

  async def glob(self: Self, pattern: str) -> AsyncIterable[Self]:
    for path in await to_thread(super().glob, pattern):
      yield AsyncPath(path)

  async def group(self) -> int:
    return await to_thread(self._path.group)

  async def hardlink_to(
    self,
    target: Self,
  ):
    return await to_thread(super().hardlink_to, target)

  async def is_block_device(self) -> bool:
    return await to_thread(self._path.is_block_device)

  async def is_char_device(self) -> bool:
    return await to_thread(self._path.is_char_device)

  async def is_dir(self) -> bool:
    return await to_thread(self._path.is_dir)

  async def is_fifo(self) -> bool:
    return await to_thread(self._path.is_fifo)

  async def is_file(self) -> bool:
    return await to_thread(self._path.is_file)

  async def is_mount(self) -> bool:
    return await to_thread(self._path.is_mount)

  async def is_socket(self) -> bool:
    return await to_thread(self._path.is_socket)

  async def is_symlink(self) -> bool:
    return await to_thread(self._path.is_symlink)

  async def iterdir(self: Self) -> AsyncIterable[Self]:
    for path in await to_thread(super().iterdir):
      yield AsyncPath(path)

  async def lstat(self) -> stat_result:
    return await to_thread(self._path.lstat)

  async def match(self, path_pattern: str) -> bool:
    return await to_thread(super().match, path_pattern)

  async def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False):
    return await to_thread(super().mkdir, mode, parents, exist_ok)

  async def owner(self) -> str:
    return await to_thread(self._path.owner)

  async def read_bytes(self) -> bytes:
    return await to_thread(self._path.read_bytes)

  async def read_text(self, encoding: str | None = None, errors: str | None = None) -> str:
    return await to_thread(self._path.read_text, encoding, errors)

  async def readlink(self: Self) -> Self:
    path: Path = await to_thread(super().readlink)
    return AsyncPath(path)

  async def rename(self, target: str | Path):
    return await to_thread(super().rename, target)

  async def replace(self: Self, target: str | PurePath) -> Self:
    path: Path = await to_thread(super().replace, target)
    return AsyncPath(path)

  async def resolve(self: Self, strict: bool = False) -> Self:
    path: Path = await to_thread(super().resolve, strict)
    return AsyncPath(path)

  async def rglob(self: Self, pattern: str) -> AsyncIterable[Self]:
    for path in await to_thread(super().rglob, pattern):
      yield AsyncPath(path)

  async def rmdir(self):
    return await to_thread(super().rmdir)

  async def samefile(self, other_path: str | bytes | Path) -> bool:
    return await to_thread(self._path.samefile, other_path)

  async def symlink_to(self, target: str | Path, target_is_directory: bool = False):
    return await to_thread(super().symlink_to, target, target_is_directory)

  async def touch(self, mode: int = 0o666, exist_ok: bool = True):
    return await to_thread(super().touch, mode, exist_ok)

  async def unlink(self, missing_ok: bool = False):
    return await to_thread(super().unlink, missing_ok)

  async def write_bytes(self, data: bytes):
    return await to_thread(self._path.write_bytes, data)

  async def write_text(self, data: str, encoding: str | None = None, errors: str | None = None, new_line: str | None = None):
    return await to_thread(self._path.write_text, data, encoding, errors, new_line)
