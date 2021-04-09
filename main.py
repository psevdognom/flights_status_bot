import asyncio

from aiogram import executor
from tortoise import Tortoise, run_async

from tg_bot.loader import dp
from tg_bot.bot import start
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
        await vnukovo_updater.update()
        print('bui')
        await asyncio.sleep(120)

async def main():
    await init_db()



if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # asyncio.run(main())

    # dp.loop.create_task(main())
    dp.loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)
