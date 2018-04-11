import time
import serial


class COM(object):
    def __init__(self, _id, port_name, timeout, baud_rate):
        self._id = _id
        self._port = port_name
        self._timeout = timeout
        self._baud_rate = baud_rate

    @property
    def port(self):
        return self._port


class FTDICOM(COM):
    def __init__(self, vend_prod_id, port_name, timeout=1.0, baud_rate=9600):
        import ftd2xx
        # set up ftdi library for loading the specified device
        ftd2xx.setVIDPID(*vend_prod_id)  # this argument is a tuple, so we unpack it
        tmp = ftd2xx.open(port_name)  # can't assign member variables before init. Oh well
        tmp.setBaudRate(9600)
        # tmp.setTimeouts(15, 50)
        serial_number = tmp.eeRead().SerialNumber

        COM.__init__(self, serial_number, port_name, timeout, baud_rate)
        self._dev = tmp

    def serial_number(self):
        # if this fails, the device has been unplugged!
        return self._dev.eeRead().SerialNumber.decode()

    def send_message(self, message):
        try:
            self._dev.write(message[0].encode())
            time.sleep(0.05)
            if message[1]:
                n_bytes = self._dev.getQueueStatus()
                resp = self._dev.read(n_bytes)
                return resp.decode()
            else:
                return ""
        except Exception as e:
            if e.message() == 'DEVICE_NOT_FOUND':
                pass
            elif e.message() == 'some other error':
                pass
            else:
                print(e.message())
            return ""

    def get_device_id(self):
        return self.serial_number()


class SerialCOM(COM):
    def __init__(self, arduino_id, port_name, timeout=1.0, baud_rate=115200):
        """Summary

        Args:
            arduino_id (TYPE): Description
        """
        COM.__init__(self, arduino_id, port_name, timeout, baud_rate)

        self._ser = serial.Serial(self._port, baudrate=self._baud_rate, timeout=self._timeout)

        time.sleep(1.0)

    def close(self):
        self._ser.close()

    def get_device_id(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._id

    def get_port(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._port

    def send_message(self, message):
        """Summary

        Args:
            message (TYPE): Description

        Returns:
            TYPE: Description
        """

        try:

            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()

            self._ser.write(message[0].encode())

            # Our own 'readline()' function
            response = b''

            if message[1]:

                start_time = time.time()
                while not (time.time() - start_time) > self._timeout:
                    resp = self._ser.read(1)
                    if resp:
                        response += bytes(resp)
                        if resp in [b'\n', b'\r']:
                            break
                        elif resp == b';':
                            # Handle MFC Readout (read in two more bytes for checksum and break)
                            response += bytes(self._ser.read(2))
                            break
                else:  # thanks, python
                    response += b'TIMEOUT'

            else:
                response += b"Didn't wait :P"

            if len(response) != 0:
                return response.decode()

        except Exception as e:
            raise Exception("Something's wrong! Exception in SerialCOM: {}".format(e))

        return ""


if __name__ == "__main__":
    pass
