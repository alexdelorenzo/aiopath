#!/usr/bin/env python3
from pathlib import Path
import asyncio

from asynctempfile import NamedTemporaryFile
import pytest

from aiopath import AsyncPath


# @pytest.mark.asyncio
async def test_home(event_loop):
  home = Path.home()
  ahome = await AsyncPath.home()

  assert str(home) == str(ahome)
  assert home.exists() == await ahome.exists()
