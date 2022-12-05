import asyncio

from aiogram import executor
from tortoise import Tortoise, run_async

from tg_bot.bot import dp
from updaters import Updater


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['models']}
    )
    sheremetievo_updater = Updater('SVO')
    vnukovo_updater = Updater('VKO')
    domodedovo_updater = Updater('DME')
    while True:
        await sheremetievo_updater.update()
        await domodedovo_updater.update()
        # await vnukovo_updater.update()
        await asyncio.sleep(120)

async def main():
    await init_db()



if __name__ == '__main__':
    dp.loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)