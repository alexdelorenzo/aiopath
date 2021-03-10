from typing import Callable, Awaitable, AsyncIterable, Iterable, \
  Any
from os import scandir, DirEntry, stat_result
from dataclasses import dataclass

from .wrap import to_thread

try:
  from asyncio import to_thread

except ImportError:
  pass


class DirWrapper:
  __slots__ = "entry",

  def __init__(self, entry: DirEntry):
    self.entry = entry

  def __getattr__(self, attr: str) -> Any:
    return getattr(self.entry, attr)

  def __repr__(self) -> str:
    name = type(self).__name__
    return f"{name}<{self.entry}>"

  async def inode(self) -> int:
    return await to_thread(self.entry.inode)

  async def is_dir(self, *, follow_symlinks: bool = True) -> bool:
    return await to_thread(self.entry.is_dir, follow_symlinks=follow_symlinks)

  async def is_file(self, *, follow_symlinks: bool = True) -> bool:
    return await to_thread(self.entry.is_file, follow_symlinks=follow_symlinks)

  async def is_symlink(self) -> bool:
    return await to_thread(self.entry.is_symlink)

  async def stat(self, *, follow_symlinks: bool = True) -> stat_result:
    return await to_thread(self.entry.stat, follow_symlinks=follow_symlinks)


def scandir_async(*args, **kwargs) -> Iterable[DirWrapper]:
  entries = scandir(*args, **kwargs)
  yield from map(DirWrapper, entries)
