from __future__ import annotations
from pathlib import PosixPath, WindowsPath, _NormalAccessor, \
  Path, PurePath, _ignore_error
from typing import Optional, List, Union, AsyncIterable, \
  Literal, Final
from os import stat_result
from stat import S_ISDIR, S_ISLNK, S_ISREG, S_ISSOCK, S_ISBLK, \
  S_ISCHR, S_ISFIFO
import os

from aiofile import AIOFile
from aiofiles import os as async_os
from aiofiles.os import wrap as method_as_method_coro, \
  wrap as func_as_corofunc

from .selectors import _make_selector
from .flavours import _async_windows_flavour, _async_posix_flavour
from .wrap import coro_as_method_coro, func_as_method_coro, to_thread
from .handle import IterableAIOFile, read_full_file
from .scandir import EntryWrapper, scandir_async


DEFAULT_ENCODING: Final[str] = 'utf-8'
ON_ERRORS: Final[str] = 'ignore'
NEWLINE: Final[str] = '\n'


TextMode = \
  Literal['r', 'w', 'a', 'x', 'r+', 'w+', 'a+', 'x+']
BinaryMode = \
  Literal['rb', 'wb', 'ab', 'xb', 'r+b', 'w+b', 'a+b', 'x+b']
FileMode = Union[TextMode, BinaryMode]


getcwd = func_as_corofunc(os.getcwd)
close = func_as_corofunc(os.close)


class _AsyncAccessor(_NormalAccessor):
  stat = coro_as_method_coro(async_os.stat)
  lstat = func_as_method_coro(os.lstat)
  open = func_as_method_coro(os.open)
  listdir = func_as_method_coro(os.listdir)
  chmod = func_as_method_coro(os.chmod)

  if hasattr(_NormalAccessor, 'lchmod'):
    lchmod = method_as_method_coro(_NormalAccessor.lchmod)

  mkdir = coro_as_method_coro(async_os.mkdir)
  unlink = func_as_method_coro(os.unlink)

  if hasattr(_NormalAccessor, 'link'):
    link = method_as_method_coro(_NormalAccessor.link)

  rmdir = coro_as_method_coro(async_os.rmdir)
  rename = coro_as_method_coro(async_os.rename)
  replace = func_as_method_coro(os.replace)

  symlink = staticmethod(
    method_as_method_coro(_NormalAccessor.symlink)
  )

  utime = func_as_method_coro(os.utime)
  readlink = method_as_method_coro(_NormalAccessor.readlink)
  remove = coro_as_method_coro(async_os.remove)

  async def owner(self, path: str) -> str:
    try:
      import pwd

      stat = await self.stat(path)
      return pwd.getpwuid(stat.st_uid).pw_name

    except ImportError:
      raise NotImplementedError("Path.owner() is unsupported on this system")

  async def group(self, path: str) -> str:
    try:
      import grp

      stat = await self.stat(path)
      return grp.getgrgid(stat.st_gid).gr_name

    except ImportError:
      raise NotImplementedError("Path.group() is unsupported on this system")

  async def scandir(self, *args, **kwargs) -> AsyncIterable[EntryWrapper]:
    async for entry in scandir_async(*args, **kwargs):
      yield entry


_async_accessor = _AsyncAccessor()


class AsyncPurePath(PurePath):
  def _init(self, template: Optional[PurePath] = None):
    self._accessor = _async_accessor

  def __new__(cls, *args):
    if cls is AsyncPurePath:
      cls = PureAsyncWindowsPath if os.name == 'nt' else PureAsyncPosixPath
    return cls._from_parts(args)


class PureAsyncPosixPath(AsyncPurePath):
  """PurePath subclass for non-Windows systems.
  On a POSIX system, instantiating a PurePath should return this object.
  However, you can also instantiate it directly on any system.
  """
  _flavour = _async_posix_flavour
  __slots__ = ()


class PureAsyncWindowsPath(AsyncPurePath):
  """PurePath subclass for Windows systems.
  On a Windows system, instantiating a PurePath should return this object.
  However, you can also instantiate it directly on any system.
  """
  _flavour = _async_windows_flavour
  __slots__ = ()


class AsyncPath(Path, AsyncPurePath):
  _flavour = \
    _async_windows_flavour if os.name == 'nt' else _async_posix_flavour
  _accessor = _async_accessor

  def _init(self, template: Optional[AsyncPath] = None):
    self._accessor = _async_accessor

  def __new__(cls, *args, **kwargs):
    if cls is AsyncPath:
      cls = AsyncWindowsPath if os.name == 'nt' else AsyncPosixPath

    self = cls._from_parts(args, init=False)

    if not self._flavour.is_supported:
      name: str = cls.__name__
      raise NotImplementedError(f"cannot instantiate {name} on your system")

    self._init()
    return self

  @property
  def _path(self) -> str:
    return str(self)

  def open(
    self,
    mode: FileMode = 'r',
    buffering: int = -1,
    encoding: Optional[str] = DEFAULT_ENCODING,
    errors: Optional[str] = ON_ERRORS,
    newline: Optional[str] = NEWLINE,
  ) -> IterableAIOFile:
    return IterableAIOFile(
      self._path,
      mode,
      encoding=encoding,
      errors=errors,
      newline=newline,
    )

  async def read_text(
    self,
    encoding: Optional[str] = DEFAULT_ENCODING,
    errors: Optional[str] = ON_ERRORS
  ) -> str:

    async with self.open('r', encoding=encoding, errors=errors) as file:
      return await file.read_text(encoding=encoding, errors=errors)

    #path = str(await self.resolve())

    #return await read_full_file(
      #path,
      #encoding=encoding,
      #errors=errors
    #)

  async def read_bytes(self) -> bytes:
    async with self.open('rb') as file:
      return await file.read()

  async def write_bytes(self, data: bytes) -> int:
    """
    Open the file in bytes mode, write to it, and close the file.
    """
    # type-check for the buffer interface before truncating the file
    view = memoryview(data)

    async with self.open(mode='wb') as f:
      return await f.write(data)

  async def write_text(
    self,
    data: str,
    encoding: Optional[str] = DEFAULT_ENCODING,
    errors: Optional[str] = ON_ERRORS,
    newline: Optional[str] = NEWLINE
  ) -> int:
    """
    Open the file in text mode, write to it, and close the file.
    """
    if not isinstance(data, str):
      raise TypeError(f'data must be str, not {type(data).__name__}')

    async with self.open(
      mode='w',
      encoding=encoding,
      errors=errors,
      newline=newline
    ) as f:
      return await f.write(data)

  async def readlink(self) -> AsyncPath:
    """
    Return the path to which the symbolic link points.
    """
    path: str = await self._accessor.readlink(self)
    obj = self._from_parts((path,), init=False)
    obj._init(template=self)
    return obj

  async def _raw_open(self, flags: int, mode: int = 0o777) -> int:
    """
    Open the file pointed by this path and return a file descriptor,
    as os.open() does.
    """
    return await self._accessor.open(self, flags, mode)

  async def touch(self, mode: int = 0o666, exist_ok: bool = True):
    """
    Create this file with the given access mode, if it doesn't exist.
    """
    if exist_ok:
      # First try to bump modification time
      # Implementation note: GNU touch uses the UTIME_NOW option of
      # the utimensat() / futimens() functions.
      try:
        await self._accessor.utime(self, None)

      except OSError:
        # Avoid exception chaining
        pass

      else:
        return

    flags: int = os.O_CREAT | os.O_WRONLY

    if not exist_ok:
      flags |= os.O_EXCL

    fd = await self._raw_open(flags, mode)
    await close(fd)

  async def mkdir(
    self,
    mode: int = 0o777,
    parents: bool = False,
    exist_ok: bool = False
  ):
    """
    Create a new directory at this given path.
    """
    try:
      await self._accessor.mkdir(self, mode)

    except FileNotFoundError:
      if not parents or self.parent == self:
        raise
      await self.parent.mkdir(parents=True, exist_ok=True)
      await self.mkdir(mode, parents=False, exist_ok=exist_ok)

    except OSError:
      # Cannot rely on checking for EEXIST, since the operating system
      # could give priority to other errors like EACCES or EROFS
      if not exist_ok or not await self.is_dir():
        raise

  async def chmod(self, mode: int):
    """
    Change the permissions of the path, like os.chmod().
    """
    await self._accessor.chmod(self, mode)

  async def lchmod(self, mode: int):
    """
    Like chmod(), except if the path points to a symlink, the symlink's
    permissions are changed, rather than its target's.
    """
    await self._accessor.lchmod(self, mode)

  async def unlink(self, missing_ok: bool = False):
    """
    Remove this file or link.
    If the path is a directory, use rmdir() instead.
    """
    try:
      await self._accessor.unlink(self)

    except FileNotFoundError:
      if not missing_ok:
        raise

  async def rmdir(self):
    """
    Remove this directory.  The directory must be empty.
    """
    await self._accessor.rmdir(self)

  async def link_to(self, target: str):
    """
    Create a hard link pointing to a path named target.
    """
    await self._accessor.link_to(self, target)

  async def rename(self, target: Union[str, AsyncPath]) -> AsyncPath:
    """
    Rename this path to the target path.
    The target path may be absolute or relative. Relative paths are
    interpreted relative to the current working directory, *not* the
    directory of the Path object.
    Returns the new Path instance pointing to the target path.
    """
    await self._accessor.rename(self, target)
    return type(self)(target)

  async def replace(self, target: str) -> AsyncPath:
    """
    Rename this path to the target path, overwriting if that path exists.
    The target path may be absolute or relative. Relative paths are
    interpreted relative to the current working directory, *not* the
    directory of the Path object.
    Returns the new Path instance pointing to the target path.
    """
    await self._accessor.replace(self, target)
    return type(self)(target)

  async def symlink_to(self, target: str, target_is_directory: bool = False):
    """
    Make this path a symlink pointing to the given path.
    Note the order of arguments (self, target) is the reverse of os.symlink's.
    """
    await self._accessor.symlink(target, self, target_is_directory)

  async def exists(self) -> bool:
    """
    Whether this path exists.
    """
    try:
      await self.stat()

    except OSError as e:
      if not _ignore_error(e):
        raise

      return False

    except ValueError:
      # Non-encodable path
      return False

    return True

  #async def exists(self) -> bool:
    #try:
      #async with async_open(self._path, 'rb'):
        #pass

      #return True

    #except IsADirectoryError:
      #return True

    #except FileNotFoundError:
      #return False

  @classmethod
  async def cwd(cls: type) -> str:
    """Return a new path pointing to the current working directory
    (as returned by os.getcwd()).
    """
    cwd: str = await getcwd()
    return cls(cwd)

  @classmethod
  async def home(cls) -> AsyncPath:
    """Return a new path pointing to the user's home directory (as
    returned by os.path.expanduser('~')).
    """
    coro = cls()._flavour.gethomedir(None)
    homedir: str = await coro

    return cls(homedir)

  async def samefile(self, other_path: Union[AsyncPath, Path]) -> bool:
    """Return whether other_path is the same or not as this file
    (as returned by os.path.samefile()).
    """
    if isinstance(other_path, AsyncPath):
      try:
        other_st = await other_path.stat()

      except AttributeError:
        other_st = await self._accessor.stat(other_path)

    else:
      try:
        other_st = await to_thread(other_path.stat)

      except AttributeError:
        other_st = await to_thread(self._accessor.stat, other_path)

    return os.path.samestat(
      await self.stat(),
      other_st
    )

  async def iterdir(self) -> AsyncIterable[AsyncPath]:
    """Iterate over the files in this directory.  Does not yield any
    result for the special paths '.' and '..'.
    """
    for name in await self._accessor.listdir(self):
      if name in {'.', '..'}:
        # Yielding a path object for these makes little sense
        continue

      yield self._make_child_relpath(name)

  async def glob(self, pattern: str) -> AsyncIterable[AsyncPath]:
    """Iterate over this subtree and yield all existing files (of any
    kind, including directories) matching the given relative pattern.
    """
    if not pattern:
      raise ValueError("Unacceptable pattern: {!r}".format(pattern))

    drv, root, pattern_parts = self._flavour.parse_parts((pattern,))

    if drv or root:
      raise NotImplementedError("Non-relative patterns are unsupported")

    selector = _make_selector(tuple(pattern_parts), self._flavour)

    async for p in selector.select_from(self):
      yield p

  async def rglob(self, pattern: str) -> AsyncIterable[AsyncPath]:
    """Recursively yield all existing files (of any kind, including
    directories) matching the given relative pattern, anywhere in
    this subtree.
    """
    drv, root, pattern_parts = self._flavour.parse_parts((pattern,))

    if drv or root:
      raise NotImplementedError("Non-relative patterns are unsupported")

    #selector = _make_selector(("**",) + tuple(pattern_parts), self._flavour)
    parts = ("**", *pattern_parts)
    selector = _make_selector(parts, self._flavour)

    async for p in selector.select_from(self):
      yield p

  async def absolute(self):
    """Return an absolute version of this path.  This function works
    even if the path doesn't point to anything.
    No normalization is done, i.e. all '.' and '..' will be kept along.
    Use resolve() to get the canonical path to a file.
    """
    # XXX untested yet!
    if self.is_absolute():
        return self
    # FIXME this must defer to the specific flavour (and, under Windows,
    # use nt._getfullpathname())
    obj = self._from_parts([await getcwd()] + self._parts, init=False)
    obj._init(template=self)
    return obj

  async def resolve(self, strict: bool = False) -> AsyncPath:
    """
    Make the path absolute, resolving all symlinks on the way and also
    normalizing it (for example turning slashes into backslashes under
    Windows).
    """
    s: Optional[str] = await self._flavour.resolve(self, strict=strict)

    if s is None:
      # No symlink resolution => for consistency, raise an error if
      # the path doesn't exist or is forbidden
      await self.stat()
      path = await self.absolute()
      s = str(path)

    # Now we have no symlinks in the path, it's safe to normalize it.
    normed: str = self._flavour.pathmod.normpath(s)
    obj = self._from_parts((normed,), init=False)
    obj._init(template=self)
    return obj

  async def stat(self) -> stat_result:
    """
    Return the result of the stat() system call on this path, like
    os.stat() does.
    """
    return await self._accessor.stat(self)

  async def lstat(self) -> stat_result:
    """
    Like stat(), except if the path points to a symlink, the symlink's
    status information is returned, rather than its target's.
    """
    return await self._accessor.lstat(self)

  async def owner(self) -> str:
    """
    Return the login name of the file owner.
    """
    return await self._accessor.owner(self)

  async def group(self) -> str:
    """
    Return the group name of the file gid.
    """
    return await self._accessor.group(self)

  async def is_dir(self) -> bool:
    """
    Whether this path is a directory.
    """
    try:
      stat = await self.stat()
      return S_ISDIR(stat.st_mode)

    except OSError as e:
      if not _ignore_error(e):
        raise

      # Path doesn't exist or is a broken symlink
      # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
      return False

    except ValueError:
      # Non-encodable path
      return False

  async def is_symlink(self) -> bool:
    """
    Whether this path is a symbolic link.
    """
    try:
      lstat = await self.lstat()
      return S_ISLNK(lstat.st_mode)

    except OSError as e:
      if not _ignore_error(e):
        raise
      # Path doesn't exist
      return False

    except ValueError:
      # Non-encodable path
      return False

  async def is_file(self) -> bool:
    """
    Whether this path is a regular file (also True for symlinks pointing
    to regular files).
    """
    try:
      stat = await self.stat()
      return S_ISREG(stat.st_mode)

    except OSError as e:
      if not _ignore_error(e):
        raise

      # Path doesn't exist or is a broken symlink
      # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
      return False

    except ValueError:
      # Non-encodable path
      return False

  async def is_mount(self) -> bool:
    """
    Check if this path is a POSIX mount point
    """
    # Need to exist and be a dir
    if not await self.exists() or not await self.is_dir():
      return False

    try:
      parent_stat = await self.parent.stat()
      parent_dev = parent_stat.st_dev

    except OSError:
      return False

    stat = await self.stat()
    dev = stat.st_dev

    if dev != parent_dev:
      return True

    ino = stat.st_ino
    parent_ino = parent_stat.st_ino

    return ino == parent_ino

  async def is_block_device(self) -> bool:
    """
    Whether this path is a block device.
    """
    try:
      stat = await self.stat()
      return S_ISBLK(stat.st_mode)

    except OSError as e:
      if not _ignore_error(e):
        raise

      # Path doesn't exist or is a broken symlink
      # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
      return False

    except ValueError:
      # Non-encodable path
      return False

  async def is_char_device(self) -> bool:
    """
    Whether this path is a character device.
    """
    try:
      stat = await self.stat()
      return S_ISCHR(stat.st_mode)
    except OSError as e:
      if not _ignore_error(e):
        raise
      # Path doesn't exist or is a broken symlink
      # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
      return False
    except ValueError:
      # Non-encodable path
      return False

  async def is_fifo(self) -> bool:
    """
    Whether this path is a FIFO.
    """
    try:
      stat = await self.stat()
      return S_ISFIFO(stat.st_mode)
    except OSError as e:
      if not _ignore_error(e):
        raise
      # Path doesn't exist or is a broken symlink
      # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
      return False
    except ValueError:
      # Non-encodable path
      return False

  async def is_socket(self) -> bool:
    """
    Whether this path is a socket.
    """
    try:
      stat = await self.stat()
      return S_ISSOCK(stat.st_mode)
    except OSError as e:
      if not _ignore_error(e):
        raise
      # Path doesn't exist or is a broken symlink
      # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
      return False
    except ValueError:
      # Non-encodable path
      return False

  async def expanduser(self) -> AsyncPath:
    """ Return a new path with expanded ~ and ~user constructs
    (as returned by os.path.expanduser)
    """
    if (not (self._drv or self._root) and
      self._parts and self._parts[0][:1] == '~'
    ):
      homedir = await self._flavour.gethomedir(self._parts[0][1:])
      return self._from_parts([homedir] + self._parts[1:])

    return self

  async def iterdir(self) -> AsyncIterable[AsyncPath]:
    names = await self._accessor.listdir(self)

    for name in names:
      if name in {'.', '..'}:
        continue

      yield self._make_child_relpath(name)


class AsyncPosixPath(PosixPath, AsyncPath, PureAsyncPosixPath):
  __slots__ = ()


class AsyncWindowsPath(WindowsPath, AsyncPath, PureAsyncWindowsPath):
  __slots__ = ()

  async def is_mount(self) -> int:
    raise NotImplementedError("AsyncPath.is_mount() is unsupported on this system")
