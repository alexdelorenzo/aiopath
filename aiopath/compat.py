# From Python 3.10.8's pathlib.py
# Source: https://github.com/python/cpython/blob/3.10/Lib/pathlib.py

from __future__ import annotations
from os import stat_result
import os, io


class _Accessor:
  """An accessor implements a particular (system-specific or not) way of
  accessing paths on the filesystem."""


class _NormalAccessor(_Accessor):
  stat = os.stat
  open = io.open
  listdir = os.listdir
  scandir = os.scandir
  chmod = os.chmod
  mkdir = os.mkdir
  unlink = os.unlink

  if hasattr(os, "link"):
    link = os.link
  else:
    def link(self, src, dst):
      raise NotImplementedError("os.link() not available on this system")

  rmdir = os.rmdir
  rename = os.rename
  replace = os.replace

  if hasattr(os, "symlink"):
    symlink = os.symlink
  else:
    def symlink(self, src, dst, target_is_directory=False):
      raise NotImplementedError("os.symlink() not available on this system")

  def touch(self, path, mode=0o666, exist_ok=True):
    if exist_ok:
      # First try to bump modification time
      # Implementation note: GNU touch uses the UTIME_NOW option of
      # the utimensat() / futimens() functions.
      try:
        os.utime(path, None)
      except OSError:
        # Avoid exception chaining
        pass
      else:
        return
    flags = os.O_CREAT | os.O_WRONLY
    if not exist_ok:
      flags |= os.O_EXCL
    fd = os.open(path, flags, mode)
    os.close(fd)

  if hasattr(os, "readlink"):
    readlink = os.readlink
  else:
    def readlink(self, path):
      raise NotImplementedError("os.readlink() not available on this system")

  def owner(self, path):
    try:
      import pwd
      return pwd.getpwuid(self.stat(path).st_uid).pw_name
    except ImportError:
      raise NotImplementedError("Path.owner() is unsupported on this system")

  def group(self, path):
    try:
      import grp
      return grp.getgrgid(self.stat(path).st_gid).gr_name
    except ImportError:
      raise NotImplementedError("Path.group() is unsupported on this system")

  getcwd = os.getcwd
  expanduser = staticmethod(os.path.expanduser)
  realpath = staticmethod(os.path.realpath)
