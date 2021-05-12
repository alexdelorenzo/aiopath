from typing import Literal, Final


TextMode = \
  Literal['r', 'w', 'a', 'x', 'r+', 'w+', 'a+', 'x+']
BinaryMode = \
  Literal['rb', 'wb', 'ab', 'xb', 'r+b', 'w+b', 'a+b', 'x+b']
FileMode = TextMode | BinaryMode
