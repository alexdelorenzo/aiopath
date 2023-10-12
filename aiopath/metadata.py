from inspect import getdoc
from typing import Any

from .types import Decoratable, Decorated, Decorator, Method


def docs_from(obj: Any) -> Decorator:
  """Use the docs from `obj` to decorate `func()`."""

  def decorator(func: Decoratable) -> Decorated:
    name: str = func.__name__

    method: Method = getattr(obj, name)
    docs: str = getdoc(method)

    func.__doc__ = docs

    return func

  return decorator
