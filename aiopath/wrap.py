from types import MethodType, FunctionType, BuiltinFunctionType, BuiltinMethodType
from typing import Callable, Any, Awaitable, Protocol
from inspect import iscoroutinefunction
from functools import wraps
from asyncio import to_thread

from aiofiles.os import \
  wrap as method_to_async_method, \
  wrap as func_to_async_func


CoroutineResult = Awaitable[Any]
CoroutineFunction = Callable[..., CoroutineResult]
CoroutineMethod = Callable[..., CoroutineResult]


class CallableObj(Protocol):
  def __call__(self, *args, **kwargs) -> Any:
    ...


def func_to_async_method(func: Callable) -> CoroutineMethod:
  @wraps(func)
  async def method(self, *args, **kwargs) -> Any:
    return await to_thread(func, *args, **kwargs)

  return method


def coro_to_async_method(coro: CoroutineFunction) -> CoroutineMethod:
  @wraps(coro)
  async def method(self, *args, **kwargs) -> Any:
    return await coro(*args, **kwargs)

  return method


def to_async_method(func: Callable) -> CoroutineMethod:
  if iscoroutinefunction(func):
    return coro_to_async_method(func)

  match func:
    case FunctionType() | BuiltinFunctionType() | CallableObj():
      return func_to_async_method(func)

    case MethodType() | BuiltinMethodType():
      return method_to_async_method(func)

  raise TypeError(f'{type(func).__name__} is not a callable.')
