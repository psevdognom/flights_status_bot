from typing import List, Optional, Type

from tortoise.models import Model
from tortoise import fields, Tortoise, run_async
from tortoise.signals import pre_delete

from tg_bot.loader import bot
from tg_bot.messages import MESSAGES


class Flight(Model):
    number = fields.CharField(max_length=12, null=True, blank=True, unique=True)
    airport = fields.CharField(max_length=30, null=True, blank=True)
    arrival_airport = fields.CharField(max_length=30, blank=True, null=True)
    gate = fields.CharField(max_length=30, null=True, blank=True)
    time_changed = fields.BooleanField(default=False)
    gate_changed = fields.BooleanField(default=False)
    departure_time = fields.DatetimeField(auto_now=False)
    on_board_time = fields.DatetimeField(auto_now=False, null=True)
    last_updated = fields.DatetimeField(auto_now=True)
    on_board_start_sent = fields.BooleanField(default=False)

    @property
    def flight_info_message(self):
        if self.gate:
            return MESSAGES['flight_info'].format(number=self.number, gate=self.gate, time=self.on_board_time)
        else:
            return MESSAGES['flight_info_no_gate_message'].format(number=self.number, time=self.on_board_time)

    @property
    def gate_changed_message(self):
        return MESSAGES['gate_changed_message'].format(number=self.number,  gate=self.gate)

    @property
    def time_changed_message(self):
        return MESSAGES['time_changed_message'].format(number=self.number, time=self.on_board_time)

    @property
    def time_and_gate_changed_message(self):
        return MESSAGES['time_and_gate_changed_message'].format(number=self.number, gate=self.gate, time=self.on_board_time)

    @property
    def has_departed(self):
        return MESSAGES['flight_has_departed'].format(number=self.number)

    @property
    def on_board_finish(self):
        return MESSAGES['on_board_finish_message'].format(number=self.number)

    @property
    def on_board_start(self):
        if self.gate:
            return MESSAGES['on_board_start_message'].format(number=self.number, gate=self.gate)
        else:
            return MESSAGES['on_board_start_no_gate_message'].format(number=self.number)

    def __str__(self):
        return self.number

    def __repr__(self):
        return self.number

    async def notify_subscribers(self, message):
        try:
            subscribers = [flight_to_chat_id.chat_id
                           for flight_to_chat_id in await FlightToChatId.filter(flight=self.number).all()]
        except Exception:
            subscribers = []
        if subscribers:
            for subscriber in subscribers:
                await bot.send_message(chat_id=subscriber, text=message)

@pre_delete(Flight)
async def signal_pre_delete(
        sender: "Type[Signal]", instance: Flight, using_db: "Optional[BaseDBAsyncClient]"
) -> None:
    await FlightToChatId.filter(flight=instance).all().delete()


class FlightToChatId(Model):
    chat_id = fields.CharField(max_length=50, null=True, blank=True)
    flight = fields.ForeignKeyField('models.Flight', on_delete=fields.SET_NULL, null=True, to_field='number', db_column='flight_id')
    created_date = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f'{self.chat_id} - {self.flight}'

    class Meta:
        table = 'flight_to_chatid'
