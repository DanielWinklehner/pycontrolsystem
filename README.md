# pycontrolsystem

## Introduction
Python-based control system with QT-based GUI class and separate server class to
talk to peripheral devices like Arduino, Teensy, power supplies, etc.

## Installation
The _spec-file.txt_ in the root folder contains an Anaconda environment with all
the dependencies of the pycontrolsystem. After installing Anaconda3, the following can
be used in Windows from a Anaconda command prompt:

`conda create --name pycontrolsystem --file spec-file.txt`

or using the __Import__ button in _Anaconda Navigator_.  

_Note: If you are using Anaconda, do the following steps in a shell openend with the 
Anaconda environment created for the pycontrolsystem._

The only module not available from Anaconda is `pyusb`. Install it simply by using pip

`pip install pyusb`

Either use pip to install the pycontrolsystem directly from the github 
repository

`pip install git+https://github.com/DanielWinklehner/pycontrolsystem.git`

or download the source first

`git clone https://github.com/DanielWinklehner/pycontrolsystem.git`

then, navigate to the pycontrolsystem folder containing _setup.py_ and run

`python setup.py install` 

## Simple Example
In the example folder, there are three files:

_server_example.py_  
_client_example.py_  
_2TestDevices.txt_

Copy them into a test directory. From your Anaconda shell start the server with

`python server_example.py`  

The server in the server example is actually just a simple dummy server returning a 
cos(t) signal for any channel queried for. It knows two devices (with ID's 
_Dummy1_ and _Dummy2_). Then start the GUI with  

`python client_example.py`  

In the Client GUI, click __Load Session__ and load the _2TestDevices.txt_ file. 
In the __Devices__ tab, one click on the different devices and cannels and see the ID's
and other parameters.

## Changing the GUI using PyQt5
_Note: This is just a random assortment of useful hints for GUI modifications_

### pyuic
In order to generate python files from QtDesigner-generated .ui files use the 
following command from an Anaconda shell (assuming pyqt >= 5.0.0 is installed):

`python -m PyQt5.uic.pyuic UIFile.ui -o ui_PythonFile.py`
