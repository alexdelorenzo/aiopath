from typing import Optional, List, Union, AsyncIterable

try:
  from typing import Literal, Final


  TextMode = \
    Literal['r', 'w', 'a', 'x', 'r+', 'w+', 'a+', 'x+']
  BinaryMode = \
    Literal['rb', 'wb', 'ab', 'xb', 'r+b', 'w+b', 'a+b', 'x+b']
  FileMode = Union[TextMode, BinaryMode]

except ImportError:
  from typing import TypeVar, Generic


  T = TypeVar('T')


  class Final(Generic[T]):
    pass

  class Literal(Generic[T]):
    pass


  FileMode = Literal[str]
