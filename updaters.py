from asyncio import sleep
from datetime import datetime

from tortoise.transactions import atomic, in_transaction

from models import Flight
from parsers import Parser
from tg_bot.loader import bot

class Updater:

    # объект для сохранения информации о рейсах и их обновлении
    # в __init__ передается код аэропорта 3 буквы
    # сначала удаляется отправленные рейсы и уведомляются их подписчики в тг
    # затем происходит вызов парсера и получения новых рейсов
    # затем происходит уведомлени старте посадки
    # при сохранении отлавливаются изменения и отправляются подпсчикам

    def __init__(self, airport_code):
        self._airport_code = airport_code

    async def delete_departed_flights(self):
        old_flights = await Flight.filter(airport=self._airport_code).filter(departure_time__lt=datetime.now()).all()
        for old_flight in old_flights:
            await old_flight.notify_subscribers(old_flight.has_departed)
            await old_flight.delete()

    async def notify_on_board_start(self):
        flights = await Flight.filter(airport=self._airport_code).filter(on_board_time__lt=datetime.now())\
            .filter(on_board_start_sent=False).all()
        for flight in flights:
            await flight.notify_subscribers(flight.on_board_start)
            flight.on_board_start_sent = True
            await flight.save()


    async def upadte_flights(self):
        airport_code = self._airport_code
        if airport_code == 'VKO':
            self._parser = Parser('http://www.vnukovo.ru/flights/online-timetable/#tab-sortie')
        elif airport_code == 'DME':
            self._parser = Parser('https://www.dme.ru/book')
        elif airport_code == 'SVO':
            self._parser = Parser('https://www.svo.aero/bitrix/')
        new_flights = await self._parser.flights
        for flight in new_flights:
            old_flight = await Flight.filter(number=flight.number).first()
            if old_flight:
                if old_flight.gate != flight.gate and old_flight.on_board_time == flight.on_board_time:
                    old_flight.gate_changed = True
                    old_flight.gate = flight.gate
                    await old_flight.save()
                    await old_flight.notify_subscribers(flight.gate_changed_message)
                elif old_flight.on_board_time != flight.on_board_time and old_flight.gate == flight.gate:
                    old_flight.time_changed = True
                    old_flight.on_board_time = flight.on_board_time
                    await old_flight.save()
                    await old_flight.notify_subscribers(flight.time_changed_message)
                elif old_flight.gate != flight.gate and old_flight.on_board_time != flight.on_board_time:
                    old_flight.time_changed = True
                    old_flight.on_board_time = flight.on_board_time
                    old_flight.gate_changed = True
                    old_flight.gate = flight.gate
                    await old_flight.save()
                    await old_flight.notify_subscribers(flight.time_and_gate_changed_message)
            else:
                await flight.save()

    # async def delete_old_flights(self):
    #     #удаление старых рейсов  где время вылета старше 2 часов
    #     pass

    async def update(self):
        await self.delete_departed_flights()
        await self.notify_on_board_start()
        await self.upadte_flights()
        await self.delete_departed_flights()
