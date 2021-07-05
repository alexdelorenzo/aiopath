#!/usr/bin/env pytest
from pathlib import Path, PurePath
from asyncio import sleep, to_thread
from os import PathLike

from asynctempfile import NamedTemporaryFile, \
  TemporaryDirectory
import pytest

from aiopath import AsyncPath, AsyncPurePath


TEST_NAME: str = 'TEST'
TEST_SUFFIX: str = f'.{TEST_NAME}'
TOUCH_SLEEP: int = 1
RECURSIVE_GLOB: str = '**/*'
WILDCARD_GLOB: str = '*'
NO_PATHS: int = 0


PathTypes = PathLike | str
Paths = tuple[Path, AsyncPath]


def get_paths(path: PathTypes) -> Paths:
  return Path(path), AsyncPath(path)


@pytest.fixture
async def file_paths() -> Paths:
  async with NamedTemporaryFile() as temp:
    yield get_paths(temp.name)


@pytest.fixture
async def file_paths() -> Paths:
  async with NamedTemporaryFile() as temp:
    yield get_paths(temp.name)


@pytest.fixture
async def dir_paths() -> Paths:
  async with TemporaryDirectory() as temp:
    yield get_paths(temp)


def _test_is_pure(
  path: Path,
  apath: AsyncPath,
):
  # PurePath & AsyncPurePath methods are not async
  assert str(path) == str(apath)
  assert path.name == apath.name
  assert path.drive == apath.drive
  assert path.root == apath.root
  assert path.stem == apath.stem
  assert path.suffix == apath.suffix
  assert path.suffixes == apath.suffixes
  assert path.as_uri() == apath.as_uri()
  assert path.is_absolute() == apath.is_absolute()
  assert path.is_reserved() == apath.is_reserved()


async def _test_is_io(
  path: Path,
  apath: AsyncPath,
):
  # AsyncPath methods are async
  assert path.exists() == await apath.exists()
  assert path.is_dir() == await apath.is_dir()
  assert path.is_file() == await apath.is_file()
  assert path.is_fifo() == await apath.is_fifo()
  assert path.is_mount() == await apath.is_mount()
  assert path.is_socket() == await apath.is_socket()
  assert path.is_symlink() == await apath.is_symlink()
  assert path.is_char_device() == await apath.is_char_device()
  assert path.is_block_device() == await apath.is_block_device()


async def _test_is(
  path: Path,
  apath: AsyncPath,
  exists: bool = True,
  resolve: bool = False,
  test_parent: bool = True,
):
  _test_is_pure(path, apath)
  await _test_is_io(path, apath)

  if exists and resolve:
    await _test_is(
      path.resolve(),
      await apath.resolve(),
      test_parent=False,
      resolve=False
    )

  if exists:
    assert path.lstat() == await apath.lstat()
    assert path.owner() == await apath.owner()
    assert path.group() == await apath.group()
    aname, pname = str(apath), str(path)
    assert path.samefile(aname) and await apath.samefile(pname)

  if test_parent:
    await _test_is(
      path.parent,
      apath.parent,
      exists=exists,
      resolve=resolve,
      test_parent=False,
    )


@pytest.mark.asyncio
async def test_home():
  home = Path.home()
  ahome = await AsyncPath.home()

  await _test_is(home, ahome)


@pytest.mark.asyncio
async def test_directory(dir_paths: Paths):
  await _test_is(*dir_paths)


@pytest.mark.asyncio
async def test_file(file_paths: Paths):
  await _test_is(*file_paths)


@pytest.mark.asyncio
async def test_mkdir_rmdir(dir_paths: Paths):
  path, apath = dir_paths

  new_name: str = 'temp_dir_test'
  new_apath = apath / new_name
  new_path = path / new_name

  await new_apath.mkdir()
  assert await new_apath.exists()
  await _test_is(new_path, new_apath)

  await new_apath.rmdir()

  assert not await new_apath.exists()
  assert not new_path.exists()
  await _test_is(new_path, new_apath, exists=False)


@pytest.mark.asyncio
async def test_with_name_with_suffix(file_paths: Paths):
  path, apath = file_paths

  await _test_is(
    path.with_suffix(TEST_SUFFIX),
    apath.with_suffix(TEST_SUFFIX),
    test_parent=False,
    exists=False
  )

  await _test_is(
    path.with_name(TEST_NAME),
    apath.with_name(TEST_NAME),
    test_parent=False,
    exists=False
  )


@pytest.mark.asyncio
async def test_write_read_text(file_paths: Paths):
  path, apath = file_paths

  text: str = 'example'
  await apath.write_text(text)
  result: str = await apath.read_text()

  assert result == text


@pytest.mark.asyncio
async def test_write_read_bytes(file_paths: Paths):
  path, apath = file_paths

  content: bytes = b'example'
  await apath.write_bytes(content)
  result: bytes = await apath.read_bytes()

  assert result == content


@pytest.mark.asyncio
async def test_touch(dir_paths: Paths):
  path, apath = dir_paths
  file = path / TEST_NAME
  afile = apath / TEST_NAME

  assert not await afile.exists()
  await afile.touch()
  assert await afile.exists()


@pytest.mark.asyncio
async def test_stat(file_paths: Paths):
  path, apath = file_paths
  stat = await apath.stat()

  await sleep(TOUCH_SLEEP)
  await apath.touch()

  new_stat = await apath.stat()

  # stat.st_ctime should be different
  assert not new_stat == stat


@pytest.mark.asyncio
async def test_unlink(file_paths: Paths, dir_paths: Paths):
  path, apath = file_paths

  assert await apath.exists()
  assert path.exists()

  await apath.unlink()
  assert not await apath.exists()
  assert not path.exists()

  # recreate file
  await apath.touch()

  path, apath = dir_paths

  assert await apath.exists() == path.exists()
  assert await apath.exists()
  assert path.exists()

  with pytest.raises(IsADirectoryError):
    await apath.unlink()


@pytest.mark.asyncio
async def test_readme_example1_basic():
  async with NamedTemporaryFile() as temp:
    path, apath = get_paths(temp.name)

    # check existence
    ## sync
    assert path.exists()
    ## async
    assert await apath.exists()

    # check if file
    ## sync
    assert path.is_file()
    ## async
    assert await apath.is_file()

    # touch
    path.touch()
    await apath.touch()

    # PurePath methods are not async
    assert path.is_absolute() == apath.is_absolute()
    assert path.as_uri() == apath.as_uri()

    # read and write text
    text: str = 'example'
    await apath.write_text(text)
    assert await apath.read_text() == text

  assert not path.exists()
  assert not await apath.exists()


@pytest.mark.asyncio
async def test_readme_example2_convert():
  home: Path = Path.home()
  ahome: AsyncPath = AsyncPath(home)
  path: Path = Path(ahome)

  assert isinstance(home, Path)
  assert isinstance(ahome, AsyncPath)
  assert isinstance(path, Path)

  # AsyncPath and Path objects can point to the same file
  assert str(home) == str(ahome) == str(path)

  # but AsyncPath and Path objects are not equivalent
  assert not home == ahome


@pytest.mark.asyncio
async def test_readme_example3_class_hierarchy():
  assert issubclass(AsyncPath, Path)
  assert issubclass(AsyncPath, PurePath)
  assert issubclass(AsyncPath, AsyncPurePath)
  assert issubclass(AsyncPurePath, PurePath)

  path: AsyncPath = await AsyncPath.home()

  assert isinstance(path, Path)
  assert isinstance(path, PurePath)
  assert isinstance(path, AsyncPurePath)


@pytest.mark.asyncio
async def test_readme_example4_read_write():
  text: str = 'example'

  async with NamedTemporaryFile() as temp:
    path = AsyncPath(temp.name)

    async with path.open(mode='w') as file:
      await file.write(text)

    async with path.open(mode='r') as file:
      result: str = await file.read()

    assert result == text

  async with NamedTemporaryFile() as temp:
    path = AsyncPath(temp.name)

    await path.write_text(text)
    result: str = await path.read_text()
    assert result == text

    content: bytes = text.encode()

    await path.write_bytes(content)
    result: bytes = await path.read_bytes()
    assert result == content


@pytest.mark.asyncio
async def test_readme_example5_glob():
  home: AsyncPath = await AsyncPath.home()

  async for path in home.glob(WILDCARD_GLOB):
    assert isinstance(path, AsyncPath)

  pkg_dir = AsyncPath(__file__).parent
  assert await pkg_dir.exists()

  paths = [path async for path in pkg_dir.glob(RECURSIVE_GLOB)]
  assert len(paths) > NO_PATHS


@pytest.mark.asyncio
async def test_rglob():
  pass


@pytest.mark.asyncio
async def test_open():
  pass



@pytest.mark.asyncio
async def test_symlink():
  pass
