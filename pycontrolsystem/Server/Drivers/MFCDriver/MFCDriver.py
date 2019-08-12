from __future__ import division


class MFCDriver:
    def __init__(self):
        self.command_dict = {"baud_rate": 'CC', "address": 'CA', "user_tag": 'UT', "operating_mode": 'OM',
                             "programmed_gas_table_size": 'GTS', "programmed_gas_table_search": 'GL',
                             "activate_programmed_gas": 'PG', "flow_units": 'U', "full_scale_range": 'FS', "wink": 'WK',
                             "run_hours_meter": 'RH', "auto_zero": "AZ", "high_trip_point": "H",
                             "high_high_trip_point": "HH",
                             "low_trip_point": "L", "low_low_trip_point": "LL", "indicated_flow_rate_percent": "F",
                             "indicated_flow_rate_units": "FX", "flow_totalizer": "FT", "status": "T",
                             "status_reset": "SR",
                             "gas_name_or_number_search": "GN", "gas_code_number": "SGN", "device_type": "DT",
                             "valve_type": "VT",
                             "valve_power_off_state": "VPO", "manafacturer": "MF", "model_designation": "MD",
                             "serial_number": "SN", "internal_temperature": "TA", "standard_temperature": "ST",
                             "standard_pressure": "SP", "control_mode": "CM", "set_point_percent": "S",
                             "set_point_units": "SX",
                             "freeze_mode": "FM", "softstart_rate": "SS", "valve_override": "VO",
                             "valve_drive_level": "VD"}

    @staticmethod
    def get_error(error_code):
        error_dict = {'01': "Checksum error", '10': "Syntax error", '11': "Data length error", '12': "Invalid data",
                      '13': "Invalid operating mode", '14': "Invalid action", '15': "Invalid gas",
                      '16': "Invalid control mode", '17': "Invalid command", '24': "Calibration error",
                      '25': "Flow too large", '27': "Too many gases in gas table",
                      '28': "Flow cal error; valve not open",
                      '98': "Internal device error", '99': "Internal device error"}
        return error_dict[str(error_code)]

    def tests(self):
        assert self.calculate_checksum("@001UT!TEST;") == "16"

    @staticmethod
    def calculate_checksum(message):

        checksum = sum(map(ord, [message_part for message_part in message]))

        return hex(checksum)[-2:].upper()

    def parse_message(self, message):

        assert message[0:3] == "@" * 3
        assert message[3:6] == "0" * 3
        assert message[-3] == ";"

        checksum = message[-2:]

        assert (checksum == self.calculate_checksum(message[:-2])) or (checksum == "FF")

        response = message[6:9]

        if response == "ACK":

            response_value = message[9:-3]

            return {'acknowledged': True, 'value': response_value}

        elif response == "NAK":

            response_value = message[9:-3]

            return {'acknowledged': False, 'value': response_value}

    def build_message(self, msg_type, device_address="254", for_what="wink", value=None, data_type=None):
        """
        :param msg_type: True for set message and False for query message
        :param device_address:
        :param for_what:
        :param value:
        :param data_type:
        :return:
        """

        msg = "@"
        msg += str(device_address)

        assert (len(str(device_address)) == 3)

        msg += self.command_dict[for_what]

        if msg_type:
            msg += "!"
        else:
            msg += "?"

        if value is not None and msg_type:
            # Handle the numerical values
            if data_type in ["<class 'bool'>", "<type 'bool'>"]:
                if value == 1.0:
                    msg += 'ON'
                else:
                    msg += 'OFF'
            elif data_type in ["<class 'float'>", "<type 'float'>"]:
                msg += "{}".format(value)
            else:
                # (int) maybe?
                pass

        msg += ";"
        msg += self.calculate_checksum(msg)
        msg = "@@" + msg

        return msg

    @staticmethod
    def get_driver_name():
        return "mfc"

    def translate_gui_to_device(self, server_to_driver):

        # --- For reference: --- #
        # device_data = {'device_driver': device_driver_name,
        #                'device_id': device_id,
        #                'locked_by_server': False,
        #                'channel_ids': [channel_ids],
        #                'precisions': [precisions],
        #                'values': [values],
        #                'data_types': [types]}

        num_of_mesg = len(server_to_driver['channel_ids'])
        assert num_of_mesg == len(server_to_driver['precisions'])
        assert server_to_driver['device_driver'] == "RS485"

        drivers_response_to_server = []

        for i in range(num_of_mesg):
            drivers_response_to_server.append(
                (self.build_message(msg_type=server_to_driver['set'],
                                    device_address=server_to_driver['device_id'],
                                    for_what=server_to_driver['channel_ids'][i],
                                    value=server_to_driver['values'][i],
                                    data_type=server_to_driver['data_types'][i]),
                 1))

        return drivers_response_to_server

    def translate_device_to_gui(self, responses, device_data):

        drivers_response_to_server = {}

        for response, channel_id in zip(responses, device_data['channel_ids']):

            parsed_message = self.parse_message(response)

            if parsed_message['acknowledged']:

                drivers_response_to_server[channel_id] = float(parsed_message['value'])
                # print(parsed_message['value'])

            else:

                drivers_response_to_server[channel_id] = "Error: " + self.get_error(parsed_message['value'])

        return drivers_response_to_server


if __name__ == '__main__':
    message_to_driver = {"channel_ids": ["wink", "wink", "wink", "wink"], "device_driver": "mfc", "set": False,
                         "precisions": [1, 2, 3, 4], "device_id": "254"}

    response_from_driver = ["@@@000ACK90.00;FF", "@@@000ACK90.00;FF", "@@@000ACK90.00;FF", "@@@000NAK13;FF"]

    x = MFCDriver()
    x.tests()
    print(x.translate_gui_to_device(message_to_driver))
    print(x.translate_device_to_gui(response_from_driver, message_to_driver))
