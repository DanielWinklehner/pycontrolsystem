from __future__ import division

import struct


class CODriver:
    def __init__(self):
        self.command_dict = {'VGET': 'VM', 'VSET': 'VCN',
                             'IGET': 'IM', 'ISET': 'ICN',
                             'SW': 'SW'}

    @staticmethod
    def parse_message(_message):
        # print('got message {}'.format(_message))
        # message comes back as "CH1=XXXX\r". Remove 'CH1=' and '\r'
        message = ''
        if _message != '':
            message = _message.strip().split('=')[1]

            perc = float(message) / 100.0

        if message != '':
            return {'acknowledged': True, 'value': perc}
        else:
            return {'acknowledged': True, 'value': 0.0}

    def build_message(self, device_id, msg_type, for_what="OUT", value=None, data_type=None):

        msg = '#{} '.format(device_id)
        msg += self.command_dict[for_what]

        if value is not None:
            # Handle the numerical values
            if self.command_dict[for_what] == 'SW':
                if value == 1.0:
                    msg += '1'
                else:
                    msg += '0'
            elif 'float' in data_type:
                msg += " {0:.2f}".format(value)  # power supply ignores values > 2 decimal points
            else:
                pass

        msg += ' \r'

        return msg

    @staticmethod
    def get_driver_name():
        return "MATSUSADA"

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
        assert server_to_driver['device_driver'] == "MATSUSADA"

        # Each message contains a flag whether we wait for a response
        device_id = server_to_driver['device_id']
        #drivers_response_to_server = [('#{} REN \r'.format(device_id), 0)]
        drivers_response_to_server = [('#AL REN \r', 0)]

        for i in range(num_of_mesg):
            drivers_response_to_server.append(
                (self.build_message(device_id=device_id,
                                    msg_type=server_to_driver['set'],
                                    for_what=server_to_driver['channel_ids'][i],
                                    value=server_to_driver['values'][i],
                                    data_type=server_to_driver['data_types'][i]),
                 not server_to_driver['set']))

        return drivers_response_to_server

    def translate_device_to_gui(self, responses, device_data):
        drivers_response_to_server = {}
        for response, channel_id in zip(responses[1:], device_data['channel_ids']):
            parsed_message = self.parse_message(response)
            if parsed_message['acknowledged']:
                drivers_response_to_server[channel_id] = float(parsed_message['value'])
            else:
                drivers_response_to_server[channel_id] = "Error: " + self.get_error(parsed_message['value'])

        return drivers_response_to_server


if __name__ == '__main__':
    message_to_driver = {"channel_ids": ["PV", "PC", "OUT"], "device_driver": "tdk", "set": False,
                         "precisions": [1, 2, 3], "device_id": "254"}

    response_from_driver = ["OK", "OK", "OK"]

    x = REKDriver()
    x.tests()
    print(x.translate_gui_to_device(message_to_driver))
    print(x.translate_device_to_gui(response_from_driver, message_to_driver))
