from functools import partial, wraps
from inspect import iscoroutinefunction
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Any, Awaitable, Callable, Protocol, runtime_checkable, NoReturn

from anyio.to_thread import run_sync

from .types import Decoratable, Decorated


type CoroutineResult[T] = Awaitable[T | None]
type CoroutineFunction[**P, T] = Callable[P, CoroutineResult[T]]
type CoroutineMethod[**P, T] = Callable[[Any, P], CoroutineResult[T]]


@runtime_checkable
class IsCallable[T](Protocol):
  def __call__(self, *args, **kwargs) -> T:
    ...


async def to_thread[**P, T](func: Decoratable, *args: P.args, **kwargs: P.kwargs) -> T:
  # anyio's run_sync() doesn't support passing kwargs
  func_kwargs: Decorated[P.args, T] = partial(func, **kwargs)
  return await run_sync(func_kwargs, *args)


def func_to_async_func[**P, T](func: Decoratable) -> CoroutineFunction:
  @wraps(func)
  async def new_func(*args: P.args, **kwargs: P.kwargs) -> T:
    return await to_thread(func, *args, **kwargs)

  return new_func


method_to_async_method: Callable[[Decoratable], CoroutineFunction] = \
  func_to_async_func


def func_to_async_method[**P, T](func: Decoratable) -> CoroutineMethod:
  @wraps(func)
  async def method(self, *args: P.args, **kwargs: P.kwargs) -> T:
    return await to_thread(func, *args, **kwargs)

  return method


def coro_to_async_method[**P, T](coro: CoroutineFunction) -> CoroutineMethod:
  @wraps(coro)
  async def method(self, *args: P.args, **kwargs: P.kwargs) -> T:
    return await coro(*args, **kwargs)

  return method


def to_async_method(func: Decoratable) -> CoroutineMethod | NoReturn:
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
