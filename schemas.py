from marshmallow import Schema, fields, post_load, pre_load

from models import Flight
# from parsers import Parser

from tortoise import Tortoise, run_async
import asyncio
import datetime

class SheremetievoCompanySchema(Schema):
    code = fields.String(required=False, allow_none=True)

class SheremetievoSchema(Schema):
    t_boarding_start = fields.String(required=False, allow_none=True)
    t_st = fields.String(required=False)
    t_st_mar = fields.String(required=False, )
    estimated_chin_finish = fields.String(required=False, allow_none=True)
    flt = fields.String(required=False, allow_none=True)
    gate_id = fields.String(required=False, allow_none=True)
    old_gate_id = fields.String(required=False, allow_none=True)
    term = fields.String(required=False, allow_none=True)
    old_term = fields.String(required=False, allow_none=True)
    co = fields.Nested(SheremetievoCompanySchema)
    airport = fields.Method('get_airport')
    number = fields.Method('get_number')
    gate = fields.Method('get_gate')
    departure_time = fields.Method('get_departure_time')
    on_board_time = fields.Method('get_on_board_time')
    # t_boarding_start = fields.String()
    # t_bording_finish =
    # estimated_chin_finish = fields.String()

    def get_departure_time(self, instance):
        return instance['t_st']

    def get_on_board_time(self, instance):
        if instance['t_boarding_start'] and not(instance['estimated_chin_finish']):
            return instance['t_boarding_start']
        elif not(instance['t_boarding_start']) and instance['estimated_chin_finish']:
            return instance['estimated_chin_finish']

    def get_number(self, instance):
        return instance['co']['code'] + ' ' + str(instance['flt'])


    def get_gate(self, instance):
        if instance['old_gate_id'] and instance['gate_id']:
            if instance['gate_id'] != instance['old_gate_id']:
                gate_numbers = instance['gate_id']
            else:
                gate_numbers = instance['gate_id']
        elif instance['old_gate_id'] and not(instance['gate_id']):
            gate_numbers = instance['old_gate_id']
        elif not(instance['old_gate_id']) and instance['gate_id']:
            gate_numbers = instance['gate_id']
        else:
            gate_numbers = ''
        if instance['old_term'] and instance['term']:
            if instance['term'] != instance['old_term']:
                gate_term = instance['term']
            else:
                gate_term = instance['term']
        elif instance['old_term'] and not(instance['term']):
            gate_term = instance['old_term']
        elif not(instance['old_term']) and instance['term']:
            gate_term = instance['term']
        else:
            gate_term = ''
        gate = str(gate_term) + ' ' + str(gate_numbers)
        return gate

    def get_airport(self, instance):
        return 'SVO'

class SheremetievoOutputSchema(Schema):
    t_boarding_start = fields.String(required=False, allow_none=True)
    t_st = fields.String(required=False, allow_none=True)
    t_st_mar = fields.String(required=False, allow_none=True)
    estimated_chin_finish = fields.String(required=False, allow_none=True)
    airport = fields.String()
    gate_id = fields.String(required=False, allow_none=True)
    old_gate_id = fields.String(required=False, allow_none=True)
    term = fields.String(required=False, allow_none=True)
    old_term = fields.String(required=False, allow_none=True)
    number = fields.String()
    flt = fields.String(required=False, allow_none=True)
    co = fields.Nested(SheremetievoCompanySchema)
    gate = fields.String(required=False, allow_none=True)
    departure_time = fields.String(required=False, allow_none=True)
    on_board_time = fields.String(required=False, allow_none=True)
    # estimated_chin_finish = fields.String(required=False, allow_none=True)

    def get_departure_time(self, instance):
        try:
            time = datetime.datetime.strptime(instance['t_st'],
                                         '%Y-%m-%dT%H:%M:%S%z')
        except Exception:
            time = datetime.datetime.now()
        return time

    def get_on_board_time(self, instance):
        try:
            time = datetime.datetime.strptime(instance['t_boarding_start'],
                                          '%Y-%m-%dT%H:%M:%S%z')
        except Exception:
            time = datetime.datetime.strptime(instance['estimated_chin_finish'],
                                          '%Y-%m-%dT%H:%M:%S%z')
        return time

    # @pre_load
    # def get_gate(self, data, **kwargs):
    #     if data["gate_id"] != data["old_gate_id"]:
    #         data.update({"gate": data["term_gate"] + str(data["gate_id"])})
    #     else:
    #         data.update({"gate": data["term_gate"] + str(data["gate_id"])})
    #     return data

    @post_load
    def make_object(self, data, **kwargs):
        try:
            try:
                departure_time = datetime.datetime.strptime(data['t_st'],
                                         '%Y-%m-%dT%H:%M:%S%z') + datetime.timedelta(hours=3)
            except Exception:
                departure_time = datetime.datetime.now()
            try:
                on_board_time = datetime.datetime.strptime(data['t_boarding_start'],
                                          '%Y-%m-%dT%H:%M:%S%z') + datetime.timedelta(hours=3)
            except Exception:
                on_board_time = datetime.datetime.strptime(data['on_board_time'],
                                          '%Y-%m-%dT%H:%M:%S%z') + datetime.timedelta(hours=3)
            flight = Flight(airport=data['airport'],
                        number=data['number'],
                        on_board_time=on_board_time,
                        departure_time=departure_time,
                        gate=data['gate'],
                        )
            return flight
        except Exception:
            yield



class SheremetievoMainSchema(Schema):
    items = fields.List(fields.Nested(SheremetievoSchema, many=True))


class DomodedovoSchema(Schema):
    airport = fields.Method('get_airport')
    number = fields.String()
    on_board_time = fields.String()
    departure_time = fields.String()
    updated_number = fields.Method('update_number')
    updated_on_board_time = fields.Method('update_on_board')
    updated_departure_time = fields.Method('update_dep')
    info = fields.String()
    gate = fields.Method('get_gate')

    monthes = {
        'янв': 1,
        'фев': 2,
        'мар': 3,
        'апр': 4,
        'май': 5,
        'июн': 6,
        'июл': 7,
        'авг': 8,
        'сен': 9,
        'окт': 10,
        'ноя': 11,
        'дек': 12,
    }

    def get_gate(self, instance):
        if 'Выход изменен на ' in instance['info']:
            return instance['info'].split('Выход изменен на ')[1]
        elif 'Выход ' in instance['info']:
            return instance['info'].split('Выход ')[1]
        else:
            return 'Неизвестно'

    def update_on_board(self, instance):
        if instance['on_board_time'] == 'неизвестно':
            return ' '
        else:
            return instance['on_board_time']

    def update_dep(self, instance):
        temp_date = instance['departure_time'].replace('\r', '').replace('\n', '').replace('\xa0', ' ')
        return f'{temp_date.split(" ")[0]} {self.monthes[temp_date.split(" ")[1]]} {datetime.datetime.now().year} {temp_date.split(" ")[2]}'

    def update_number(self, instance):
        temp_number = instance['number'].replace('\n', '').replace('\r', '')
        return temp_number.split(' ')[0] + ' ' + temp_number.split(' ')[1]


    def get_airport(self, instance):
        return 'DME'

class DomodedovoOutputSchema(Schema):
    airport = fields.String()
    number = fields.String()
    on_board_time = fields.String()
    departure_time = fields.String()
    updated_number = fields.String()
    updated_on_board_time = fields.String(allow_none=True)
    updated_departure_time = fields.String(allow_none=True)
    info = fields.String()
    gate = fields.String(allow_none=True, required=False)

    @staticmethod
    def get_on_board_time_and_departure_from_string(data):
        departure_time = datetime.datetime(year=int(data['updated_departure_time'].split(' ')[2]),
                                           month=int(data['updated_departure_time'].split(' ')[1]),
                                           day=int(data['updated_departure_time'].split(' ')[0]),
                                           hour=int(data['updated_departure_time'].split(' ')[3].split(':')[0]),
                                           minute=int(data['updated_departure_time'].split(' ')[3].split(':')[1]))
        if data['updated_on_board_time'] == ' ':
            on_board_time = datetime.datetime.now()
        else:
            if int(departure_time.hour) > int(data['updated_on_board_time'].split(':')[0]):
                print(data['updated_departure_time'])
                on_board_time = datetime.datetime(year=int(data['updated_departure_time'].split(' ')[2]),
                                                  month=int(data['updated_departure_time'].split(' ')[1]),
                                                  day=int(data['updated_departure_time'].split(' ')[0]),
                                                  hour=int(data['updated_on_board_time'].split(':')[0]),
                                                  minute=int(data['updated_on_board_time'].split(':')[1])) \
                                - datetime.timedelta(days=1)
            else:
                on_board_time = datetime.datetime(year=int(data['updated_departure_time'].split(' ')[2]),
                                                  month=int(data['updated_departure_time'].split(' ')[1]),
                                                  day=int(data['updated_departure_time'].split(' ')[0]),
                                                  hour=int(data['updated_on_board_time'].split(':')[0]),
                                                  minute=int(data['updated_on_board_time'].split(':')[1]))

        return departure_time, on_board_time




    @post_load
    def make_object(self, data, **kwargs):
        departure_time, on_board_time = self.get_on_board_time_and_departure_from_string(data)
        if data['gate'] != 'Неизвестно':
            flight = Flight(number=data['updated_number'], on_board_time=on_board_time,
                            airport=data['airport'],
                            departure_time=departure_time,
                            gate=data['gate'])
        else:
            flight = Flight(number=data['updated_number'], on_board_time=on_board_time,
                            airport=data['airport'],
                            departure_time=departure_time)
        return flight

class VnukovoSchema(Schema):
    airport = fields.Method('get_airport')
    number = fields.String()
    flight_number = fields.String()
    on_board_time = fields.String()
    departure_time = fields.String()
    gate = fields.String(allow_none=True)

    def get_airport(self, instance):
        return 'VKO'

class VnukovoOutputSchema(Schema):
    airport = fields.String()
    number = fields.String()
    flight_number = fields.String()
    on_board_time = fields.String()
    departure_time = fields.String()
    gate = fields.String(allow_none=True)

    @staticmethod
    def get_on_board_time_and_departure_from_string(data):
        departure_time = datetime.datetime(year=int(data['departure_time'].split('.')[2]),
                                           month=int(data['departure_time'].split('.')[1]),
                                           day=int(data['departure_time'].split('.')[0][5:7]),
                                           hour=int(data['departure_time'].split(':')[0]),
                                           minute=int(data['departure_time'].split(':')[1][2:4]))
        if data['on_board_time'] == ' ':
            on_board_time = datetime.datetime.now()
        else:
            if int(departure_time.hour) < int(data['on_board_time'].split(':')[0]):
                on_board_time = datetime.datetime(year=int(data['departure_time'].split('.')[2]),
                                                  month=int(data['departure_time'].split('.')[1]),
                                                  day=int(data['departure_time'].split('.')[0][5:7])-1,
                                                  hour=int(data['on_board_time'].split(':')[0]),
                                                  minute=int(data['on_board_time'].split(':')[1]))
            else:
                on_board_time = datetime.datetime(year=int(data['departure_time'].split('.')[2]),
                                                  month=int(data['departure_time'].split('.')[1]),
                                                  day=int(data['departure_time'].split('.')[0][5:7]),
                                                  hour=int(data['on_board_time'].split(':')[0]),
                                                  minute=int(data['on_board_time'].split(':')[1][:2]))
        return departure_time, on_board_time

    @post_load
    def make_object(self, data, **kwargs):
        departure_time, on_board_time = self.get_on_board_time_and_departure_from_string(data)
        try:
            flight = Flight(number=data['number'], airport=data['airport'],
                            on_board_time=on_board_time, departure_time=departure_time, gate=data['gate'])
        except KeyError:
            flight = Flight(number=data['number'], airport=data['airport'],
                            on_board_time=on_board_time, departure_time=departure_time)
        return flight

    def get_airport(self, instance):
        return 'VKO'

class TestNestedSchema(Schema):
    name = fields.String()

class TestSchema(Schema):
    id = fields.Integer()
    company = fields.Nested(TestNestedSchema)
    company_id = fields.Method('get_company_id')

    def get_company_id(self, instance):
        return str(instance['id']) + instance['company']['name']

    @post_load
    def make_object(self):
        pass




# if __name__ == '__main__':
#     data = {'id': 1, 'dasdas':'dasd',
#             'kek': 'lol', 'company': {"dasda": "zaadsda", 'name': 'SU'}}
#
#     schema = VnukovoOutputSchema()
#     r = schema.load(data)
#     print(r)