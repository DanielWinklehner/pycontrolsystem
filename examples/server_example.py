# from pycontrolsystem.Server.DummyServer import *  # Replace DummyServer with Server to run actual hardware.
from pycontrolsystem.Server.Server import *  # Replace DummyServer with Server to run actual hardware.

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        shutdown()
