from inspect import getdoc
from typing import Any, Callable

from .types import Method


def docs_from[**P, R](
  obj: Any
) -> Callable[[Callable[P, R]], Callable[P, R]]:
  """Use the docs from `obj` to decorate `func()`."""

  def decorator(func: Callable[P, R]) -> Callable[P, R]:
    name = func.__name__
    method: Method = getattr(obj, name)
    func.__doc__ = getdoc(method)

    return func

  return decorator
