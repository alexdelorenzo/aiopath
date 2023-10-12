from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Literal, Callable


type Method[**P, T] = Callable[P, T]

type Decoratable[**P, T] = Callable[P, T]
type Decorated[**P, T] = Callable[P, T]
type Decorator = Callable[[Decoratable], Decorated]

type FileMode = TextMode | BinaryMode
type TextMode = Literal['r', 'w', 'a', 'x', 'r+', 'w+', 'a+', 'x+']
type BinaryMode = Literal['rb', 'wb', 'ab', 'xb', 'r+b', 'w+b', 'a+b', 'x+b']

type Paths = Path | PathLike | AsyncPath | AsyncPurePath | str
