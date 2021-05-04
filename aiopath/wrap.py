from typing import Callable, Any, Awaitable
from functools import wraps, partial
from inspect import ismethod, isfunction, iscoroutinefunction
from asyncio import to_thread
from types import MethodType, FunctionType, BuiltinFunctionType, BuiltinMethodType
import contextvars

from aiofiles.os import \
  wrap as method_as_method_coro, \
  wrap as func_to_async_func


CoroutineResult = Awaitable[Any]
CoroutineFunction = Callable[..., CoroutineResult]
CoroutineMethod = Callable[..., CoroutineResult]


def func_as_method_coro(func: Callable) -> CoroutineMethod:
  @wraps(func)
  async def method(self, *args, **kwargs) -> Any:
    return await to_thread(func, *args, **kwargs)

  return method


def coro_as_method_coro(coro: CoroutineFunction) -> CoroutineMethod:
  @wraps(coro)
  async def method(self, *args, **kwargs) -> Any:
    return await coro(*args, **kwargs)

  return method


def to_async_method(func: Callable) -> CoroutineMethod:
  if iscoroutinefunction(func):
    return coro_as_method_coro(func)

  match func:
    case FunctionType() | BuiltinFunctionType() | BuiltinMethodType():
      return func_as_method_coro(func)

    case MethodType():
      return method_as_method_coro(func)

  if callable(func):
    return func_as_method_coro(func)

  else:
    raise TypeError(f'{type(func).__name__} is not callable.')
