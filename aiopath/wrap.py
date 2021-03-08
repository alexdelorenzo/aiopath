from functools import wraps

try:
  from asyncio import to_thread

except ImportError:
  from asyncio import get_running_loop

  async def to_thread(func, *args, **kwargs):
    loop = get_running_loop()
    return await loop.run_in_executor(
      None,
      func,
      *args,
      **kwargs
    )


def func_as_method_coro(func):
  @wraps(func)
  async def method(self, *args, **kwargs):
    return await to_thread(func, *args, **kwargs)

  return method


def coro_as_method_coro(coro):
  @wraps(coro)
  async def method(self, *args, **kwargs):
    return await coro(*args, **kwargs)

  return method
