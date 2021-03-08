# 📁 Async pathlib for Python
`aiopath` is a complete implementation of [`pathlib`](https://docs.python.org/3/library/pathlib.html) from Python 3.4+ that is compatible with [`asyncio`](https://docs.python.org/3/library/asyncio.html) and the [`async/await` syntax](https://www.python.org/dev/peps/pep-0492/). All I/O performed is asynchronous and [awaitable](https://docs.python.org/3/library/asyncio-task.html#awaitables).

`aiopath` is extensively typed with Python [type annotations](https://docs.python.org/3/library/typing.html). `aiopath` also takes advantage of [libaio](https://pagure.io/libaio) on Linux.

## Usage
`aiopath.Path` has the same API as `pathlib.Path`, and `aiopath.AsyncPurePath` works the same way as `pathlib.PurePath`. The only difference is that with `aiopath`, methods that perform I/O are asynchronous and awaitable, and methods that returned iterators now return [async generators](https://www.python.org/dev/peps/pep-0525/).

To run the following examples with top-level `await` expressions, [launch an asynchronous Python REPL](https://www.integralist.co.uk/posts/python-asyncio/#running-async-code-in-the-repl) using `python3 -m asyncio`.

### Basic
All of `pathlib.Path`'s methods that perform synchronous I/O are reimplemented as asynchronous methods.

```python3
import tempfile
from pathlib import Path
from aiopath import AsyncPath


with tempfile.NamedTemporaryFile() as temp:
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

  # read and write text
  text = "example"
  await apath.write_text(text)
  assert text == await apath.read_text()

assert not path.exists()
assert not await apath.exists()
```

You can convert `pathlib.Path` objects to `aiopath.Path` objects easily:
```python3
from pathlib import Path
from aiopath import AsyncPath


home: Path = Path.home()
ahome: AsyncPath = AsyncPath(home)

assert isinstance(home, Path)
assert isinstance(ahome, AsyncPath)
```

### Opening a file
You can get an asynchronous [file-like object handle](https://docs.python.org/3/glossary.html#term-file-object) by using [asynchronous context managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers).

```python3
import tempfile
from aiopath import AsyncPath


text: str = 'example'

with tempfile.NamedTemporaryFile() as temp:
  apath = AsyncPath(temp.name)

  async with apath.open(mode='w') as afile:
    await afile.write(text)

  result: str = await apath.read_text()
  assert result == text
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
  # caution! this might take awhile
  paths: List[AsyncPath] = \
    [path async for path in downloads.glob('**/*')]
```

# Installation
## Dependencies
 - A POSIX compliant OS, or Windows
 - Python 3.7+
 - `requirements.txt`

## PyPI
```bash
$ python3 -m pip install aiopath
```

## GitHub
```bash
$ python3 -m pip install -r requirements.txt
$ python3 setup.py install
```

### Linux
This library will take advantage of [libaio](https://pagure.io/libaio), which is compatible with Linux 4.18 and up.

```bash
sudo apt install libaio1
```

# Support
Want to support this project and [other open-source software](https://github.com/alexdelorenzo) like this?

<a href="https://www.buymeacoffee.com/alexdelorenzo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60px" style="height: 60px !important;width: 217px !important;max-width:25%" ></a>

# License
See `LICENSE`. If you'd like to use this project with a different license, please get in touch.


# Credit
See [`CREDIT.md`](/CREDIT.md).
