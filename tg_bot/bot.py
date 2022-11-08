

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.helper import Helper, HelperMode, ListItem

from .loader import dp
from .messages import MESSAGES
from settings import BOT_TOKEN
from models import Flight, FlightToChatId


async def get_flight(flight_number):
    if flight_number:
        try:
            flight = await Flight.filter(number=flight_number).first()
            return flight.flight_info_message
        except Exception:
            return 'Такого рейса нет в системе'
    else:
        return 'Введен пустой текст'


class FlightsTimetableUserStates(Helper):
    mode = HelperMode.snake_case

    UNREGISTER = ListItem()
    ON_TRACK = ListItem()


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.reply(MESSAGES['start'])


@dp.message_handler()
async def register_flight(message: types.Message):
    flight_number = message.text
    if flight_number:
        try:
            flight = await Flight.filter(number=flight_number).first()
            flight_to_chat_id = FlightToChatId(flight=flight, chat_id=message.chat.id)
            await flight_to_chat_id.save()
            reply_message = flight.flight_info_message
        except Exception as ex:
            reply_message = 'Такого рейса нет в системе'
    else:
        reply_message = 'Введен пустой текст'
    await message.reply(reply_message)


@dp.message_handler(state=FlightsTimetableUserStates.ON_TRACK)
async def renew_info(message: types.Message):

    pass