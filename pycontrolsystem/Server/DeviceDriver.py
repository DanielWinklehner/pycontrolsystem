from Drivers import *


class DeviceDriver:
    def __init__(self,
                 driver_name=None):

        self._module_extensions = ('.py', '.pyc', '.pyo')

        self._driver_name = driver_name
        self._driver = None

        self.load_driver()

    def load_driver(self):
        self._driver = driver_mapping[self._driver_name]['driver']()

    def get_driver_name(self):
        return self._driver_name

    def translate_gui_to_device(self, data):
        return self._driver.translate_gui_to_device(data)

    def translate_device_to_gui(self, data, original_message):
        return self._driver.translate_device_to_gui(data, original_message)
