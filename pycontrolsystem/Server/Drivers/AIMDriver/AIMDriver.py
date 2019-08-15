from __future__ import division


class AIMDriver:
    def __init__(self):
        self.command_dict = {'id': 'S0',
                             'p1': 'V752',
                             'on': 'C752'}

    @staticmethod
    def parse_message(_message):
        ack = False
        print("mAIM-S message:", _message)
        if _message.startswith('*'):
            # Error response or set commend acknowledged (error code '00' = all good)
            print("Error response:", _message)
            cmd, status = _message.strip().split()
            status = int(status)
            if status == 0:
                ack = True
            else:
                print("AIMDriver received error message #{}".format(status))
        elif _message.startswith('='):
            # Query response
            # print("Query response:", _message)
            ack = True
            value, status = _message.strip().split()[1].split(';')
            value = float(value)

            gas_type = [0, 0, 0]  # Default is N2 (binary 000 = ascii 0)
            p_units = [1, 0]  # Default is Pascal (binary 10 = ascii 2)
            # TODO: This is probably wrong. I usually only receive two bytes when manually querying
            (
                mag_exp,  # Magnetron exposure threshold exceeded
                gas_type[2], gas_type[1], gas_type[0],  # Gas type in binary
                _, _,  # only used in Pirani gauges  (bits 11, 10)
                mag_str_err,  # magnetron striking failure (not struck) (bit 9)
                mag_str,  # magnetron striking (bit 8)
                calibrating,  # Calibration in progress - pressure reading invalid (bit 7)
                flash_err,  # All stored parameters and calibrations defaulted (bit 6)
                p_units[1], p_units[0],  # Pressure units in binary
                gauge_lock,  # Gauge parameters locked
                setp_on,  # Setpoint On or Off
                magn_on,  # Gauge Magnetron On or Off
                error  # Gauge specific error active (bits 6-11)
            ) = list(bin(int(status, 16))[2:].zfill(16))

        else:
            print("Could not understand gauge response!")

        if ack:
            return {'acknowledged': ack, 'value': value}
        else:
            return {'acknowledged': ack, 'value': False}

    def build_message(self, set_msg, for_what="id", value=None, data_type=None):

        if set_msg:
            msg = "!"
        else:
            msg = "?"

        msg += self.command_dict[for_what]

        if value is not None:
            msg += " {:.0f}".format(value)

        msg += '\r'

        return msg

    @staticmethod
    def get_driver_name():
        return "nAIM-S"

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
        assert server_to_driver['device_driver'] == self.get_driver_name()

        # Each message contains a flag whether we wait for a response
        drivers_response_to_server = []

        for i in range(num_of_mesg):

            drivers_response_to_server.append(
                (self.build_message(set_msg=server_to_driver['set'],
                                    for_what=server_to_driver['channel_ids'][i],
                                    value=server_to_driver['values'][i],
                                    data_type=server_to_driver['data_types'][i]),
                 not server_to_driver['set']))

        return drivers_response_to_server

    def translate_device_to_gui(self, responses, device_data):
        drivers_response_to_server = {}

        for response, channel_id in zip(responses, device_data['channel_ids']):
            parsed_message = self.parse_message(response)
            if parsed_message['acknowledged']:
                drivers_response_to_server[channel_id] = float(parsed_message['value'])
            # else:
            #     drivers_response_to_server[channel_id] = "Error: " + self.get_error(parsed_message['value'])

        return drivers_response_to_server


if __name__ == '__main__':
    message_to_driver = {"channel_ids": ["p1"],
                         "device_driver": "nAIM-S",
                         "set": False,
                         "precisions": [3],
                         "device_id": "0",
                         "values": [None],
                         "data_types": [float]}

    response_from_driver = ["=V752 1.00E-05;00\r"]  # Typical pressure response

    x = AIMDriver()

    print(x.translate_gui_to_device(message_to_driver))
    print(x.translate_device_to_gui(response_from_driver, message_to_driver))
