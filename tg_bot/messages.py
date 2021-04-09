start_message = 'Введите номер рейса для отслеживания'
flight_info = 'ИНфрмация о рейсе {number}: выход {gate} плановое время начала посадки {time}'
flight_gate_changed = '{number} выход изменен на {gate}'
flight_time_changed = '{number} время посадки изменено на {time}'
flight_time_and_gate_changed = '{number} время посадки изменено на {time} и выход изменен на {gate}'
flight_has_departed = '{number} самолет улетел'
on_board_started = '{number} посадка началась, следуйте к {gate}'
on_board_started_no_gate = '{number} посадка началась'
on_board_finished = '{number} посадка окончена'
flight_info_no_gate = 'ИНфрмация о рейсе {number}: плановое время начала посадки {time}'

MESSAGES = {
    'start': start_message,
    'gate_changed_message':  flight_gate_changed,
    'time_changed_message': flight_time_changed,
    'time_and_gate_changed_message': flight_time_and_gate_changed,
    'flight_has_departed': flight_has_departed,
    'flight_info': flight_info,
    'on_board_finish_message': on_board_finished,
    'on_board_start_message': on_board_started,
    'on_board_start_no_gate_message': on_board_started_no_gate,
    'flight_info_no_gate_message': flight_info_no_gate,
    }