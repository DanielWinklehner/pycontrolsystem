from .ArduinoDriver import *
from .MFCDriver import *
from .TDKDriver import *
from .REKDriver import *
from .CODriver import *

"""
The driver mapping contains the information needed for the DeviceDriver class and the RasPiServer to
use the respective translation functions from GUI to Device and back and the correct baud rate
"""
driver_mapping = {'Arduino': {'driver': ArduinoDriver,
                              'baud_rate': 115200
                              },
                  'RS485': {'driver': MFCDriver,
                            'baud_rate': 9600
                            },
                  'Teensy': {'driver': ArduinoDriver,
                             'baud_rate': 115200
                             },
                  'FT232R': {'driver': TDKDriver,
                             'baud_rate': 19200
                             },
                  'Prolific': {'driver': REKDriver,
                               'baud_rate': 9600
                               },
                  # TODO: Changed this from CO Series to match a Windows accessible description in DeviceFinder
                  # TODO: But we have to think about fthe serial number thing now...
                  'MATSUSADA': {'driver': CODriver,
                                'baud_rate': 9600,
                                'ftdi_info': (0x1192, 0x1000)  # VID, PID
                                },
                  }
