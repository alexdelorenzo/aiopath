# 📁 Async pathlib for Python
`aiopath` is a complete implementation of Python's [`pathlib`](https://docs.python.org/3/library/pathlib.html) that is compatible with [`asyncio`](https://docs.python.org/3/library/asyncio.html) and Python's [`async/await` syntax](https://www.python.org/dev/peps/pep-0492/). All I/O performed by `aiopath` is asynchronous and [awaitable](https://docs.python.org/3/library/asyncio-task.html#awaitables).

`aiopath` takes advantage of Python [type annotations](https://docs.python.org/3/library/typing.html), and it also takes advantage of [`libaio`](https://pagure.io/libaio) on Linux.

## Use case
If you're writing asynchronous code and want to take advantage of `pathlib`'s conveniences, but don't want to mix blocking and non-blocking I/O, then you can reach for `aiopath`.

As an example, if you're writing an asynchronous scraper, you might want to make several concurrent requests to websites, and then write the results of those requests to secondary storage:
```python3
from typing import List
from asyncio import run, gather

from aiohttp import ClientSession
from aiopath import AsyncPath


async def save_page(url: str, name: str):
  async with ClientSession() as session:
    response = await session.get(url)
    content: bytes = await response.read()

  path = AsyncPath(name)

  if not await path.exists():
    await path.write_bytes(content)


async def main():
  urls: List[str] = [
    'https://example.com',
    'https://github.com/alexdelorenzo/aiopath',
    'https://alexdelorenzo.dev'
  ]

  scrapers = (save_page(url, f"{index}.html") for index, url in enumerate(urls))
  return await gather(*scrapers)


run(main())
```
If you used `pathlib` instead of `aiopath` in the example above, tasks would block upon writing to the disk, and tasks that make network connections would be forced to pause while other tasks write to the disk.

By using `aiopath`, all I/O is non-blocking, and your script can simultaneously write to the disk and perform network operations at once.

# Usage
`aiopath` is a direct reimplementation of [CPython's `pathlib.py`](https://github.com/python/cpython/blob/master/Lib/pathlib.py), and `aiopath`'s class hierarchy [directly matches the one from `pathlib`](https://docs.python.org/3/library/pathlib.html), where `Path` inherits from `PurePath`, `AsyncPath` inherits from `AsyncPurePath`, and so on.

With `aiopath`, methods that perform I/O are asynchronous and awaitable, and methods that perform I/O and return iterators in `pathlib` now return [async generators](https://www.python.org/dev/peps/pep-0525/).

## Examples
### Running examples
To run the following examples with top-level `await` expressions, [launch an asynchronous Python REPL](https://www.integralist.co.uk/posts/python-asyncio/#running-async-code-in-the-repl) using `python3 -m asyncio`.

You'll also need to install `asynctempfile` via PyPI, like so `python3 -m pip install asynctempfile`

### Basic
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
  assert text == await apath.read_text()

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
assert str(home) == str(ahome) == str(path)
```

### Opening a file
You can get an asynchronous [file-like object handle](https://docs.python.org/3/glossary.html#term-file-object) by using [asynchronous context managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers).

```python3
from asynctempfile import NamedTemporaryFile
from aiopath import AsyncPath


text: str = 'example'

async with NamedTemporaryFile() as temp:
  apath = AsyncPath(temp.name)

  async with apath.open(mode='w') as afile:
    await afile.write(text)

  assert text == await apath.read_text()
```

### [Globbing](https://en.wikipedia.org/wiki/Glob_(programming))
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
