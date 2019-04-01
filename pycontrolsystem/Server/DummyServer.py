import sys
import json
import numpy as np
import time

from flask import Flask, request

from .DeviceDriver import driver_mapping


class DummyDevice(object):
    """
    Simple dummy that has a name, and returns a sin(x) like signal
    """
    def __init__(self, driver):
        self.serial_number = None
        self.query_message = None
        self.port = 0
        self.polling_rate = 1
        self.driver = driver

    @property
    def current_values(self):

        data = {"timestamp": time.time(),
                "polling_rate": 1.0}

        for cha in self.query_message['channel_ids']:

            data[cha] = np.cos(2.0*np.pi*time.time())

        return data

    @staticmethod
    def add_command_to_queue(cmd):
        return cmd


# /===============================\
# |                               |
# |         Flask server          |
# |                               |
# \===============================/
app = Flask(__name__)

# disable flask output messages (makes server easier to debug)
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

_mydebug = False
_keep_communicating = False
_initialized = False
_devices = {"Dummy1": DummyDevice(driver_mapping['ArduinoMega']['driver']()),
            "Dummy2": DummyDevice(driver_mapping['ArduinoMega']['driver']())}  # Create two dummy devices to query from

_current_responses = {}


@app.route("/initialize/")
def initialize():
    global _initialized
    global _keep_communicating

    if _initialized:
        return "DummyServer has already been initialized"
    else:
        _keep_communicating = True
        _initialized = True
        return "DummyServer Initialized"


@app.route("/device/set", methods=['GET', 'POST'])
def set_value_on_device():
    # Load the data stream
    set_cmd = json.loads(request.form['data'])
    set_cmd["set"] = True

    # For reference: This is the message from the GUI:
    # device_data = {'device_driver': device_driver_name,
    #                'device_id': device_id,
    #                'locked_by_server': False,
    #                'channel_ids': [channel_ids],
    #                'precisions': [precisions],
    #                'values': [values],
    #                'data_types': [types]}

    full_device_id = set_cmd['device_id']
    device_id_parts = full_device_id.split("_")
    sub_id = device_id_parts[0]
    device_id = device_id_parts[0]

    if len(device_id_parts) > 1:
        sub_id = device_id_parts[1]

    set_cmd['device_id'] = sub_id

    _devices[device_id].add_command_to_queue(set_cmd)

    return 'Command sent to device'


@app.route("/device/query", methods=['GET', 'POST'])
def query_device():
    # Load the data stream
    data = json.loads(request.form['data'])
    devices_responses = {}
    for i, device_data in enumerate(data):
        device_data['set'] = False

        # for master/slave devices, we need to send commands to the master only
        # e.g. if serial number is XXXXXX_2, we look for device XXXXXX, and
        # device data should then use only the '2' as the id.
        full_device_id = device_data['device_id']
        device_id_parts = full_device_id.split("_")
        device_id = device_id_parts[0]

        if len(device_id_parts) > 1:
            device_data['device_id'] = device_id_parts[1]

        try:
            _devices[device_id].query_message = device_data
            devices_responses[full_device_id] = _devices[device_id].current_values
        except KeyError:
            # device not found on server
            devices_responses[full_device_id] = "ERROR: Device not found on server"

    return json.dumps(devices_responses)


@app.route("/device/active/")
def all_devices():

    global _devices
    ports = {}

    for _id, dm in _devices.items():
        ports[_id] = [dm.port, dm.polling_rate, dm.driver.get_driver_name()]

    return json.dumps(ports)


def shutdown():

    global _keep_communicating

    print("Shutting down...")
    _keep_communicating = False

    sys.exit("Killed")


if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        shutdown()
