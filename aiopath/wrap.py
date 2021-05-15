from typing import Callable, Any, Awaitable
from functools import wraps, partial

from anyio.to_thread import run_sync


CoroutineResult = Awaitable[Any]
CoroutineFunction = Callable[..., CoroutineResult]
CoroutineMethod = Callable[..., CoroutineResult]


async def to_thread(func: Callable, *args, **kwargs) -> Any:
  # anyio's run_sync() doesn't support passing kwargs
  func_kwargs = partial(func, **kwargs)
  return await run_sync(func_kwargs, *args)


def func_to_async_func(func: Callable) -> CoroutineFunction:
  @wraps(func)
  async def new_func(*args, **kwargs) -> Any:
    return await to_thread(func, *args, **kwargs)

  return new_func


method_as_method_coro = func_to_async_func


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
