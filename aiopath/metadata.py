from typing import Any, Callable, ParamSpec, TypeVar
from inspect import getdoc


T = TypeVar('T')
P = ParamSpec('P')

Decoratable = Callable[P, T]
Decorated = Callable[P, T]
Decorator = Callable[[Decoratable], Decorated]

Method = Callable[P, T]


def docs_from(obj: Any) -> Decorator:
  """Use the docs from `obj` to decorate `func()`."""

  def decorator(func: Decoratable) -> Decorated:
    name: str = func.__name__

    method: Method = getattr(obj, name)
    docs: str = getdoc(method)

    func.__doc__ = docs

    return func

  return decorator
