# This file contains classes which handle locating device information
# from various sources on the server computer.

import subprocess
import usb.core
import platform

# Necessary for PyCharm because package name is 'pyserial' and import is 'serial'
# noinspection PyPackageRequirements
from serial.tools import list_ports

myplatform = platform.platform()


class DeviceFinder(object):

    def __init__(self, identifiers):
        self._identifiers = identifiers
        self._current_devices = {}
        self._name = 'BASE'

    def find_devices(self):
        raise NotImplementedError("Subclasses should implement this!")

    @property
    def identifiers(self):
        return self._identifiers

    @identifiers.setter
    def identifiers(self, val):
        self._identifiers = val

    @property
    def name(self):
        return self._name


class SerialDeviceFinderLinux(DeviceFinder):

    def __init__(self, identifiers):
        DeviceFinder.__init__(self, identifiers)
        self._name = 'serial'

    def find_devices(self):
        # _device_added = False
        # _device_removed = False

        # local dictionaries to hold intermediate values
        _device_ids = list(self._current_devices.keys())
        _found_devices_by_ids = {}
        _obsolete_devices_by_ids = {}
        _added_devices_by_ids = {}

        # this device finder opens a shell script to return device-port pairs
        proc = subprocess.Popen('/home/pi/RasPiServer_v5/usb.sh',
                                stdout=subprocess.PIPE, shell=True)

        output = proc.stdout.read().strip()

        # Loop through all found devices and add them to a new list, remove them from the current list
        for line in output.decode().split("\n"):
            # Go through all identifiers and see if one is found in this serial port
            _identifier = [identifier for identifier in self._identifiers.keys() if identifier in line]

            if len(_identifier) == 1:
                _identifier = _identifier[0]

                port, raw_info = line.split(" - ")
                serial_number = raw_info.split("_")[-1] + "_" + port  # TODO: This is a total hack. pyserial on windows
                # TODO doesn't seem to be able to return the correct serial number of a device.
                # TODO: I think we have to rethink how to uniquely address serial devices! -DW

                _found_devices_by_ids[serial_number] = {"port": port,
                                                        "identifier": _identifier}

                if serial_number not in _device_ids:
                    # _device_added = True
                    _added_devices_by_ids[serial_number] = _found_devices_by_ids[serial_number]
                else:
                    del _device_ids[_device_ids.index(serial_number)]

        # Now, let's check if there are any devices still left in the id list
        if len(_device_ids) > 0:
            # _device_removed = True
            for _id in _device_ids:
                # These SerialCOM objects have to be destroyed
                _obsolete_devices_by_ids[_id] = self._current_devices[_id]

        self._current_devices = _found_devices_by_ids

        return {'current': self._current_devices,
                'added': _added_devices_by_ids,
                'obsolete': _obsolete_devices_by_ids}


class SerialDeviceFinderWindows(DeviceFinder):

    def __init__(self, identifiers):
        DeviceFinder.__init__(self, identifiers)
        self._name = 'serial'

    def find_devices(self):
        # _device_added = False
        # _device_removed = False

        # local dictionaries to hold intermediate values
        _device_ids = list(self._current_devices.keys())
        _found_devices_by_ids = {}
        _obsolete_devices_by_ids = {}
        _added_devices_by_ids = {}

        for port_info in list_ports.comports():

            if port_info.vid is None:
                continue  # Only accepting ports with vid/pid

            # print("{}:{}".format(hex(port_info.vid), hex(port_info.pid)), ", {}".format(port_info.description))

            # Match Devices to VID/PID combination in driver_mapping

            # Go through all identifiers and see if one is found in this serial port
            _identifiers = [identifier for identifier in self._identifiers.keys() if
                            self._identifiers[identifier]["vid_pid"] == (port_info.vid, port_info.pid) and
                            port_info.serial_number in self._identifiers[identifier]["known_serials"]]

            if len(_identifiers) == 1:

                _identifier = _identifiers[0]

                port = port_info.device
                serial_number = port_info.serial_number

                _found_devices_by_ids[serial_number] = {"port": port,
                                                        "identifier": _identifier}

                if serial_number not in _device_ids:
                    # _device_added = True
                    _added_devices_by_ids[serial_number] = _found_devices_by_ids[serial_number]
                else:
                    del _device_ids[_device_ids.index(serial_number)]

        # Now, let's check if there are any devices still left in the id list
        if len(_device_ids) > 0:
            # _device_removed = True
            for _id in _device_ids:
                # These SerialCOM objects have to be destroyed
                _obsolete_devices_by_ids[_id] = self._current_devices[_id]

        self._current_devices = _found_devices_by_ids

        return {'current': self._current_devices,
                'added': _added_devices_by_ids,
                'obsolete': _obsolete_devices_by_ids}


class FTDIDeviceFinder(DeviceFinder):

    def __init__(self, identifiers):
        DeviceFinder.__init__(self, identifiers)
        self._name = 'ftdi'

        self._vend_prod_list = {}
        for name, info in self._identifiers.items():
            try:
                self._vend_prod_list[name] = info['ftdi_info']
            except KeyError:
                # driver does not have ftdi field
                pass

    def find_devices(self):
        # !!! for ftdi devices, id = address since we can't access serial
        # numbers without opening & locking the devices !!!
        _device_added = False
        _device_removed = False

        # local dictionaries to hold intermediate values
        _device_ids = list(self._current_devices.keys())
        _found_devices_by_ids = {}
        _obsolete_devices_by_ids = {}
        _added_devices_by_ids = {}

        # use PyUSB to find ftdi devices
        dev = usb.core.find(find_all=True)

        for cfg in dev:
            # look for matches with existing driver product/vendor IDs
            vend_prod = (cfg.idVendor, cfg.idProduct)
            bus_addr = (cfg.bus, cfg.address)
            bus_addr_key = '{}:{}'.format(*bus_addr)

            idf = None
            for name, vp in self._vend_prod_list.items():
                if vend_prod == vp:
                    idf = name
                    break

            if idf is None:
                continue

            _found_devices_by_ids[bus_addr_key] = {"port": '{}:{}'.format(*bus_addr),
                                                   "identifier": idf,
                                                   "vend_prod": vend_prod}

            if bus_addr_key not in _device_ids:
                _device_added = True
                _added_devices_by_ids[bus_addr_key] = _found_devices_by_ids[bus_addr_key]
            else:
                del _device_ids[_device_ids.index(bus_addr_key)]

        # Now, let's check if there are any devices still left in the id list
        if len(_device_ids) > 0:
            _device_removed = True
            for _id in _device_ids:
                # These SerialCOM objects have to be destroyed
                _obsolete_devices_by_ids[_id] = self._current_devices[_id]

        self._current_devices = _found_devices_by_ids

        return {'current': self._current_devices,
                'added': _added_devices_by_ids,
                'obsolete': _obsolete_devices_by_ids}


# Assign the SerialDeviceFinder to the respective platform
if 'Windows' in myplatform:
    SerialDeviceFinder = SerialDeviceFinderWindows
else:
    SerialDeviceFinder = SerialDeviceFinderLinux
