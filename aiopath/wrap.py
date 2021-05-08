from types import MethodType, FunctionType, \
  BuiltinFunctionType, BuiltinMethodType
from typing import Callable, Any, Awaitable, \
  Protocol
from inspect import iscoroutinefunction
from functools import wraps

from anyio.to_thread import run_sync


CoroutineResult = Awaitable[Any]
CoroutineFunction = Callable[..., CoroutineResult]
CoroutineMethod = Callable[..., CoroutineResult]


class CallableObj(Protocol):
  def __call__(self, *args, **kwargs) -> Any:
    ...


def func_to_async_func(func: Callable) -> CoroutineFunction:
  @wraps(func)
  async def new_func(*args, **kwargs) -> Any:
    return await run_sync(func, *args, **kwargs)

  return new_func


method_to_async_method = func_to_async_func
to_thread = func_to_async_func


def func_to_async_method(func: Callable) -> CoroutineMethod:
  @wraps(func)
  async def method(self, *args, **kwargs) -> Any:
    return await run_sync(func, *args, **kwargs)

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
