from __future__ import annotations
from pathlib import Path, PosixPath, WindowsPath, _NormalAccessor, \
  _Selector,_is_wildcard_pattern, _ignore_error, _Flavour
from typing import AsyncIterable, Callable, List
from os import DirEntry
import functools

from .wrap import CoroutineMethod


class _AsyncSelector:
  """A selector matches a specific glob pattern part against the children
      of a given path.
  """

  def __init__(self, child_parts: List[str], flavour: _Flavour):
    self.child_parts: List[str] = child_parts

    if child_parts:
      self.successor = _make_selector(child_parts, flavour)
      self.dironly = True

    else:
      self.successor = _TerminatingSelector()
      self.dironly = False

  async def select_from(
    self,
    parent_path: 'AsyncPath'
  ) -> AsyncIterable['AsyncPath']:
    """Iterate over all child paths of `parent_path` matched by this
    selector.  This can contain parent_path itself."""
    path_cls = type(parent_path)
    is_dir = path_cls.is_dir
    exists = path_cls.exists
    scandir = parent_path._accessor.scandir

    if not await is_dir(parent_path):
      return

    async for item in self._select_from(parent_path, is_dir, exists, scandir):
      yield item


class _TerminatingSelector:
  async def _select_from(
    self,
    parent_path: 'AsyncPath', 
    is_dir: CoroutineMethod, 
    exists: CoroutineMethod, 
    scandir: CoroutineMethod
  ) -> AsyncIterable['AsyncPath']:
    yield parent_path


class _PreciseSelector(_AsyncSelector):
  def __init__(self, name: str, child_parts: List[str], flavour: _Flavour):
    self.name: str = name
    super().__init__(child_parts, flavour)

  async def _select_from(
    self,
    parent_path: 'AsyncPath', 
    is_dir: CoroutineMethod, 
    exists: CoroutineMethod, 
    scandir: CoroutineMethod
  ) -> AsyncIterable['AsyncPath']:
    try:
      path = parent_path._make_child_relpath(self.name)

      if await (is_dir if self.dironly else exists)(path):
        async for p in self.successor._select_from(path, is_dir, exists, scandir):
          yield p
    except PermissionError:
      return


class _WildcardSelector(_AsyncSelector):
  def __init__(self, pat: str, child_parts: List[str], flavour: _Flavour):
    self.match = flavour.compile_pattern(pat)
    super().__init__(child_parts, flavour)

  async def _select_from(
    self,
    parent_path: 'AsyncPath', 
    is_dir: CoroutineMethod, 
    exists: CoroutineMethod, 
    scandir: CoroutineMethod
  ) -> AsyncIterable['AsyncPath']:
    try:
      async for entry in scandir(parent_path):
        if self.dironly:
          try:
            # "entry.is_dir()" can raise PermissionError
            # in some cases (see bpo-38894), which is not
            # among the errors ignored by _ignore_error()
            if not await entry.is_dir():
              continue
          except OSError as e:
            if not _ignore_error(e):
              raise
            continue

        name = entry.name

        if self.match(name):
          path = parent_path._make_child_relpath(name)

          async for p in self.successor._select_from(path, is_dir, exists, scandir):
            yield p
    except PermissionError:
      return


class _RecursiveWildcardSelector(_AsyncSelector):
  def __init__(self, pat: str, child_parts: List[str], flavour):
    super().__init__(child_parts, flavour)

  async def _iterate_directories(
    self,
    parent_path: 'AsyncPath', 
    is_dir: CoroutineMethod, 
    scandir: CoroutineMethod
  ) -> AsyncIterable['AsyncPath']:
    yield parent_path

    try:
      async for entry in scandir(parent_path):
        entry_is_dir: bool = False

        try:
          entry_is_dir = await entry.is_dir()

        except OSError as e:
          if not _ignore_error(e):
            raise

        if entry_is_dir and not await entry.is_symlink():
          path = parent_path._make_child_relpath(entry.name)

          async for p in self._iterate_directories(path, is_dir, scandir):
            yield p
    except PermissionError:
      return

  async def _select_from(self, parent_path, is_dir, exists, scandir) -> AsyncIterable['AsyncPath']:
    try:
      yielded = set()

      try:
        successor_select = self.successor._select_from

        async for starting_point in self._iterate_directories(parent_path, is_dir, scandir):
          async for p in successor_select(starting_point, is_dir, exists, scandir):
            if p not in yielded:
              yield p
              yielded.add(p)

      finally:
        yielded.clear()
    except PermissionError:
      return


def _make_selector(pattern_parts: List[str], flavour: _Flavour) -> _AsyncSelector:
  pat: str = pattern_parts[0]
  child_parts: List[str] = pattern_parts[1:]

  if pat == '**':
    cls = _RecursiveWildcardSelector

  elif '**' in pat:
    raise ValueError("Invalid pattern: '**' can only be an entire path component")

  elif _is_wildcard_pattern(pat):
    cls = _WildcardSelector

  else:
    cls = _PreciseSelector

  return cls(pat, child_parts, flavour)


if hasattr(functools, "lru_cache"):
  _make_selector: Callable = functools.lru_cache()(_make_selector)
