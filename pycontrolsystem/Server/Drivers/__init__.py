from .ArduinoDriver import *
from .MFCDriver import *
from .TDKDriver import *
from .REKDriver import *
from .CODriver import *

"""
The driver mapping contains the information needed for the DeviceDriver class and the RasPiServer to
use the respective translation functions from GUI to Device and back and the correct baud rate
"""
driver_mapping = {'ArduinoMicro': {'driver': ArduinoDriver,
                                   'baud_rate': 115200,
                                   'vid_pid': (0x2341, 0x8037)
                                   },
                  'ArduinoMega': {'driver': ArduinoDriver,
                                  'baud_rate': 115200,
                                  'vid_pid': (0x2341, 0x0042)
                                  },
                  'RS485': {'driver': MFCDriver,
                            'baud_rate': 9600,
                            'vid_pid': (0x0000, 0x0000)
                            },
                  'Teensy': {'driver': ArduinoDriver,
                             'baud_rate': 115200,
                             'vid_pid': (0x16C0, 0x0483)
                             },
                  'FT232R': {'driver': TDKDriver,
                             'baud_rate': 19200,
                             'vid_pid': (0x0403, 0x6001)
                             },
                  'Prolific': {'driver': REKDriver,
                               'baud_rate': 9600,
                               'vid_pid': (0x067B, 0x2303)
                               },
                  'MATSUSADA': {'driver': CODriver,
                                'baud_rate': 9600,
                                'vid_pid': (0x1192, 0x1000),
                                'ftdi_info': (0x1192, 0x1000)
                                },
                  }
