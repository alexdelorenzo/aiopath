from types import MethodType, FunctionType, \
  BuiltinFunctionType, BuiltinMethodType
from typing import Callable, Any, Awaitable, \
  Protocol, runtime_checkable
from inspect import iscoroutinefunction
from functools import wraps, partial

from anyio.to_thread import run_sync


CoroutineResult = Awaitable[Any]
CoroutineFunction = Callable[..., CoroutineResult]
CoroutineMethod = Callable[[Any, ...], CoroutineResult]


@runtime_checkable
class IsCallable(Protocol):
  def __call__(self, *args, **kwargs) -> Any:
    ...


async def to_thread(func: Callable, *args, **kwargs) -> Any:
  # anyio's run_sync() doesn't support passing kwargs
  func_kwargs = partial(func, **kwargs)
  return await run_sync(func_kwargs, *args)


def func_to_async_func(func: Callable) -> CoroutineFunction:
  @wraps(func)
  async def new_func(*args, **kwargs) -> Any:
    return await to_thread(func, *args, **kwargs)

  return new_func


method_to_async_method: Callable = func_to_async_func


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
  match func:
    case _ if iscoroutinefunction(func):
      return coro_to_async_method(func)

    case FunctionType() | BuiltinFunctionType() | IsCallable():
      return func_to_async_method(func)

    case MethodType() | BuiltinMethodType():
      return method_to_async_method(func)

    case _ if callable(func):
      return func_to_async_method(func)

  raise TypeError(f'{type(func).__name__} is not callable.')
