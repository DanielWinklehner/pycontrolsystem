from . import ArduinoMessages

class ArduinoDriver:
    def __init__(self):
        pass

    @staticmethod
    def get_driver_name():
        return "arduino"

    @staticmethod
    def translate_gui_to_device(data):

        # For reference: This is the message from the GUI:
        # device_data = {'device_driver': device_driver_name,
        #                'device_id': device_id,
        #                'locked_by_server': False,
        #                'channel_ids': [channel_ids],
        #                'precisions': [precisions],
        #                'values': [values],
        #                'data_types': [types]}

        if data['set']:
            return ArduinoMessages.build_set_message(data['channel_ids'], data['values'])
        else:
            # Query message.
            return ArduinoMessages.build_query_message(data['channel_ids'], data['precisions'])

    @staticmethod
    def translate_device_to_gui(data, device_data):
        return ArduinoMessages.parse_arduino_output_message(data)
