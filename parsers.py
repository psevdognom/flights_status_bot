from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from aiohttp import ClientSession, request
from async_property import async_property
from bs4 import BeautifulSoup

# from .models import Flight

from schemas import SheremetievoOutputSchema, VnukovoSchema, SheremetievoSchema, VnukovoOutputSchema, DomodedovoOutputSchema, DomodedovoSchema

import asyncio

class Parser(ABC):

    #объект парсер отвечает за получение данных с табло аэропортов
    # в зависимости от ссылки создается объект со своим методом получения данных
    # для добавления нового аэропорта необходимо создать свой парсер
    # полученные данные приводится к стандартному виду при помощи marshmallow
    # async property flights отдает все необходимые рейсы в виде корутин для дальнейшего сохранения
    # в __init__ прописывается время охвата расписания

    def __init__(self, link):
        self._link = link
        self._local_time = datetime.now() - timedelta(hours=3)
        self._monitor_time = self._local_time + timedelta(hours=10)
        self._schema = None
        self._output_schema = None

    def __new__(cls, link):
        if link == 'http://www.vnukovo.ru/flights/online-timetable/#tab-sortie':
            return super().__new__(VnukovoParser)
        elif 'svo.aero' in link:
            return super().__new__(SheremetievoParser)
        elif 'https://www.dme.ru/book' in link:
            return super().__new__(DomodedovoParser)

    @abstractmethod
    async def get_flights_data(self):
        pass


    async def get_page(self):
        async with ClientSession() as session:
            async with session.get(self._link, verify_ssl=False) as resp:
                return await resp.text()

    async def get_json(self):
        async with ClientSession() as session:
            async with session.get(self._link, verify_ssl=False) as resp:
                return await resp.json()


    @async_property
    async def flights(self):
        data = await self.get_flights_data()
        validated_data = list()
        for flyght_d in data:
            val_data = self._schema().dump(flyght_d)
            validated_data.append(val_data)
        flights = list()
        for flight_json in validated_data:
            flight = self._output_schema().load(flight_json)
            flights.append(flight)
        return [flight for flight in flights if flight]


class VnukovoParser(Parser):
    def __init__(self, link):
        super().__init__(link)
        self._schema = VnukovoSchema
        self._output_schema = VnukovoOutputSchema
        #self._tomorrow_link = 'http://www.vnukovo.ru/flights/online-timetable/?arDF_sf%5Bcurrent_day%5D=tomorrow&arDF_sf%5Bterm%5D=&arDF_sf%5Bcurrent_hour%5D=all&arDF_sf%5Bsf_flight%5D=&arDF_sf%5Bsf_airline%5D=&arDF_sf%5Bsf_airport%5D=&set_filter=Y'


    async def get_tomorrow_flights(self, link):
        pass

    def get_flights_from_page(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        table_rows = soup.find(id='sortie').find(name='tbody').find_all(name='tr')
        resp = []
        for row in table_rows[:-1]:
            row_data = dict()
            departure_time = row.find_all('td')[0].text
            number = row.find('a').text
            on_board_time_str = row.find_all('td')[-1].text
            try:
                on_board_time = on_board_time_str.split('Посадка с ')[1].split('</')[0]
            except Exception:
                try:
                    on_board_time = on_board_time_str.split('Окончание в ')[1].split('</')[0]
                except Exception:
                    on_board_time = 'Улетел'
            if 'Выход ' in on_board_time_str:
                gate = on_board_time_str.split('Выход')[1]
                row_data.update({'gate': gate})
            row_data.update({'number': number})
            row_data.update({'on_board_time': on_board_time})
            row_data.update({'departure_time': departure_time})
            resp.append(row_data)
        return resp

    async def get_flights_data(self):
        flights = list()
        page = await self.get_page()
        today_resp = self.get_flights_from_page(page)
        tomorrow_resp = list()
        if int(self._local_time.hour) > int(self._monitor_time.hour):
            tomorrow_page_link = 'http://www.vnukovo.ru/flights/online-timetable/?arDF_sf%5Bcurrent_day%5D=tomorrow&arDF_sf%5Bterm%5D=&arDF_sf%5Bcurrent_hour%5D=all&arDF_sf%5Bsf_flight%5D=&arDF_sf%5Bsf_airline%5D=&arDF_sf%5Bsf_airport%5D=&set_filter=Y'
            async with ClientSession() as session:
                async with session.get(tomorrow_page_link) as resp:
                    tomorrow_page = await resp.text()
                    tomorrow_resp = self.get_flights_from_page(tomorrow_page)
        for flight_dict in today_resp:
            if int(flight_dict['departure_time'].split(':')[0]) >= int(self._local_time.hour) and \
                flight_dict['on_board_time'] != "Улетел":
                flights.append(flight_dict)
        if tomorrow_resp:
            for flight_dict in tomorrow_resp:
                if int(flight_dict['departure_time'].split(':')[0]) <= int(self._monitor_time.hour):
                    flights.append(flight_dict)
        return flights








class SheremetievoParser(Parser):
    def __init__(self, link):
        super().__init__(link)
        self._schema = SheremetievoSchema
        self._output_schema = SheremetievoOutputSchema
        self._link = f"https://www.svo.aero/bitrix/timetable/?direction=departure"\
                                "&dateStart="\
                                f"{self._local_time.year}-"\
                                f"{self._local_time.month}-"\
                                f"{self._local_time.day}T"\
                                f"{self._local_time.hour}:"\
                                f"{self._local_time.minute}:00%2B03:00&"\
                                    "dateEnd="\
                                f"{self._monitor_time.year}-"\
                                f"{self._monitor_time.month}-"\
                                f"{self._monitor_time.day}T"\
                                f"{self._monitor_time.hour}:"\
                                f"{self._monitor_time.minute}:00%2B03:00&perPage=9999&page=0&locale=ru"

    async def get_flights_data(self):
        data = await self.get_json()
        return data['items']




class DomodedovoParser(Parser):
    def __init__(self, link):
        super().__init__(link)
        self._local_time = datetime.now()
        self._schema = DomodedovoSchema
        self._output_schema = DomodedovoOutputSchema
        self._link = f'https://www.dme.ru/book/live-board/?searchText=&column=4&sort=1' \
                     f'&start={24 * 60 + int(self._local_time.hour)* 60 + int(self._local_time.minute) + 40}&' \
                     f'end={24 * 60 + int(self._monitor_time.hour)* 60 + int(self._monitor_time.minute) + 24 * 60 }' \
                     f'&direction=D&page=1&count=&isSlider=1'

    async def get_flights_data(self):
        page = await self.get_page()
        soup = BeautifulSoup(page, 'html.parser')
        table_rows = soup.find('table', {'id': 'table'}).find_all('tr')
        flights = []
        for tr in table_rows[2:]:
            numbers = tr.find_all('a', {"class": "dialogopen"})
            try:
                departure_time = tr.find('td', {'nowrap': "nowrap"}).text
            except Exception:
                departure_time = 'error'
            info = tr.find('ul').find('div').text
            try:
                on_board_time = info.split('садки в ')[1].split(':')[0] +':'+info.split('садки в ')[1].split(':')[1][:2]
            except Exception:
                on_board_time = 'неизвестно'
            for flight_number in numbers:
                row_schema = dict()
                row_schema.update({'info': info})
                row_schema.update({'number': flight_number.text})
                row_schema.update({'departure_time': departure_time})
                row_schema.update({'on_board_time': on_board_time})
                flights.append(row_schema)
        print(self._link)
        return flights


class KoltsovoParser(Parser):

    def __init__(self, link):
        super().__init__(link)

    async def get_flights_data(self):
        pass


class SurgutParser(Parser):

    pass

class PulkovoParser(Parser):

    pass


async def main():

    parser = Parser('https://www.svo.aero/bitrix/')
    data = await parser.get_page()
    await parser.get_flights_data()
    flights = await parser.flights
    print(flights)
    dom_parser = Parser('https://www.dme.ru/book')
    fl = await dom_parser.get_flights_data()
    print(fl)
    vnukovo_parser = Parser('http://www.vnukovo.ru/flights/online-timetable/#tab-sortie')
    data = await vnukovo_parser.get_flights_data()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())