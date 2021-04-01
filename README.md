# 📁 Async pathlib for Python
`aiopath` is a complete implementation of Python's [`pathlib`](https://docs.python.org/3/library/pathlib.html) that's compatible with [`asyncio`](https://docs.python.org/3/library/asyncio.html) and the [`async/await` syntax](https://www.python.org/dev/peps/pep-0492/). 

All I/O performed by `aiopath` is asynchronous and [awaitable](https://docs.python.org/3/library/asyncio-task.html#awaitables).

## Use case
If you're writing asynchronous Python code and want to take advantage of `pathlib`'s conveniences, but don't want to mix blocking and [non-blocking I/O](https://en.wikipedia.org/wiki/Asynchronous_I/O), then you can reach for `aiopath`.

For example, if you're writing an asynchronous [web scraping](https://en.wikipedia.org/wiki/Web_scraping) script, you might want to make several concurrent requests to websites and write the content in the responses to secondary storage:
```python3
from typing import List
from asyncio import run, gather

from aiohttp import ClientSession
from aiopath import AsyncPath


async def save_page(url: str, name: str):
  path = AsyncPath(name)
  
  if await path.exists():
    return

  async with ClientSession() as session:
    response = await session.get(url)
    content: bytes = await response.read()

  await path.write_bytes(content)


async def main():
  urls: List[str] = [
    'https://example.com',
    'https://github.com/alexdelorenzo/aiopath',
    'https://alexdelorenzo.dev',
    'https://dupebot.firstbyte.dev'
  ]

  scrapers = (
    save_page(url, f"{index}.html")
    for index, url in enumerate(urls)
  )
  
  await gather(*scrapers)


run(main())
```
If you used `pathlib` instead of `aiopath` in the example above, some tasks would block upon writing to the disk, and the other tasks making network connections would be forced to pause while the disk is accessed.

By using `aiopath` in the example above, the script can access the network and disk concurrently.

## Implementation 
`aiopath` is a direct reimplementation of [CPython's `pathlib.py`](https://github.com/python/cpython/blob/master/Lib/pathlib.py) and shares some of its code. `aiopath`'s class hierarchy [directly matches the one from `pathlib`](https://docs.python.org/3/library/pathlib.html), where `Path` inherits from `PurePath`, `AsyncPath` inherits from `AsyncPurePath`, and so on.

With `aiopath`, methods that perform I/O are asynchronous and awaitable, and methods that perform I/O and return iterators in `pathlib` now return [async generators](https://www.python.org/dev/peps/pep-0525/). `aiopath` goes one step further, and wraps [`os.scandir()`](https://docs.python.org/3/library/os.html#os.scandir) and [`DirEntry`](https://docs.python.org/3/library/os.html#os.DirEntry) to make [`AsyncPath.glob()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob) completely async.

`aiopath` is typed with Python [type annotations](https://docs.python.org/3/library/typing.html), and it takes advantage of [`libaio`](https://pagure.io/libaio) for async I/O on Linux.

# Usage
 `aiopath`'s API directly matches [`pathlib`](https://docs.python.org/3/library/pathlib.html), so check out the standard library documentation for [`PurePath`](https://docs.python.org/3/library/pathlib.html#pure-paths) and [`Path`](https://docs.python.org/3/library/pathlib.html#methods).
 
### Running examples
To run the following examples with top-level `await` expressions, [launch an asynchronous Python REPL](https://www.integralist.co.uk/posts/python-asyncio/#running-async-code-in-the-repl) using `python3 -m asyncio` or an [IPython shell](https://ipython.org/).

You'll also need to install `asynctempfile` via PyPI, like so `python3 -m pip install asynctempfile`.

## Basic
All of `pathlib.Path`'s methods that perform synchronous I/O are reimplemented as asynchronous methods. `PurePath` methods are not asynchronous because they don't perform I/O.

```python3
from pathlib import Path

from asynctempfile import NamedTemporaryFile
from aiopath import AsyncPath


async with NamedTemporaryFile() as temp:
  path = Path(temp.name)
  apath = AsyncPath(temp.name)

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
  text: str = "example"
  await apath.write_text(text)
  assert await apath.read_text() == text

assert not path.exists()
assert not await apath.exists()
```

You can convert `pathlib.Path` objects to `aiopath.AsyncPath` objects, and vice versa:
```python3
from pathlib import Path
from aiopath import AsyncPath


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
```

## Opening a file
You can get an asynchronous [file-like object handle](https://docs.python.org/3/glossary.html#term-file-object) by using [asynchronous context managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers). 

`AsyncPath.open()`'s async context manager yields an [`aiofile.AIOFile`](https://github.com/mosquito/aiofile) object.

```python3
from asynctempfile import NamedTemporaryFile
from aiopath import AsyncPath


text: str = 'example'

# you can access a file with async context managers
async with NamedTemporaryFile() as temp:
  path = AsyncPath(temp.name)

  async with path.open(mode='w') as file:
    await file.write(text)
  
  async with path.open(mode='r') as file:
    result: str = await file.read()

  assert result == text
  
# or you can use the read/write convenience methods
async with NamedTemporaryFile() as temp:
  path = AsyncPath(temp.name)

  await path.write_text(text)
  result: str = await path.read_text()
  assert result == text
  
  content: bytes = text.encode()

  await path.write_bytes(content)
  result: bytes = await path.read_bytes()
  assert result == content
```

## [Globbing](https://en.wikipedia.org/wiki/Glob_(programming))
`aiopath` implements [`pathlib` globbing](https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob) using async I/O and async generators.

```python3
from typing import List
from aiopath import AsyncPath


home: AsyncPath = await AsyncPath.home()

async for path in home.glob('*'):
  assert isinstance(path, AsyncPath)
  print(path)

downloads: AsyncPath = home / 'Downloads'

if await downloads.exists():
  # this might take a while
  paths: List[AsyncPath] = \
    [path async for path in downloads.glob('**/*')]
```

# Installation
## Dependencies
 - A POSIX compliant OS, or Windows
 - Python 3.7+
 - `requirements.txt`

#### Linux dependencies
If you're using a 4.18 or newer kernel and have [`libaio`](https://pagure.io/libaio) installed, `aiopath` will use it via `aiofile`. You can install `libaio` on Debian/Ubuntu like so:
```bash
$ sudo apt install libaio1
```

## PyPI
```bash
$ python3 -m pip install aiopath
```

## GitHub
```bash
$ python3 -m pip install -r requirements.txt
$ python3 setup.py install
```

# Support
Want to support this project and [other open-source projects](https://github.com/alexdelorenzo) like it?

<a href="https://www.buymeacoffee.com/alexdelorenzo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60px" style="height: 60px !important;width: 217px !important;max-width:25%" ></a>

# License
See `LICENSE`. If you'd like to use this project with a different license, please get in touch.


# Credit
See [`CREDIT.md`](/CREDIT.md).
