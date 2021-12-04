from types import MethodType, FunctionType, \
  BuiltinFunctionType, BuiltinMethodType
from typing import Callable, Any, Awaitable, \
  Protocol, runtime_checkable, TypeVar, Generic, \
  NoReturn, ParamSpec
from inspect import iscoroutinefunction
from functools import wraps, partial

from anyio.to_thread import run_sync


P = ParamSpec('P')
T, S = map(TypeVar, 'TS')

CoroutineResult = Awaitable[T | None]
CoroutineFunction = Callable[P, CoroutineResult[T]]
CoroutineMethod = Callable[[Any, P], CoroutineResult[T]]


@runtime_checkable
class IsCallable(Generic[T], Protocol):
  def __call__(self, *args, **kwargs) -> T:
    ...


async def to_thread(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
  # anyio's run_sync() doesn't support passing kwargs
  func_kwargs: Callable[P.args, T] = partial(func, **kwargs)
  return await run_sync(func_kwargs, *args)


def func_to_async_func(func: Callable[P, T]) -> CoroutineFunction[P, T]:
  @wraps(func)
  async def new_func(*args: P.args, **kwargs: P.kwargs) -> T:
    return await to_thread(func, *args, **kwargs)

  return new_func


method_to_async_method: Callable[Callable[P, T], CoroutineFunction[P, T]] = \
  func_to_async_func


def func_to_async_method(func: Callable[P, T]) -> CoroutineMethod[P, T]:
  @wraps(func)
  async def method(self, *args: P.args, **kwargs: P.kwargs) -> T:
    return await to_thread(func, *args, **kwargs)

  return method


def coro_to_async_method(coro: CoroutineFunction[P, T]) -> CoroutineMethod[P, T]:
  @wraps(coro)
  async def method(self, *args: P.args, **kwargs: P.kwargs) -> T:
    return await coro(*args, **kwargs)

  return method


def to_async_method(func: Callable[P, T]) -> CoroutineMethod[P, T] | NoReturn:
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
