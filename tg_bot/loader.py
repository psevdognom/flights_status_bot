import asyncio

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import BOT_TOKEN
from pydantic.main import BaseModel
from typing import Union, Optional

loop = asyncio.get_event_loop()

bot = Bot(BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, loop=loop, storage=storage)


class Test(BaseModel):
    id: Optional[int] = None
    name: str

if __name__ == '__main__':
    executor.start_polling(dp)