#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Thomas Wester <twester@mit.edu>
#
# Code adapted from MIST1ControlSystem.py (Python 2/gtk3+ version)
import sys
import os
import requests
import json
import timeit
import time
import threading
import queue
import operator
from multiprocessing import Process, Pipe

from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog

from gui import MainWindow

from gui.dialogs.PlotChooseDialog import PlotChooseDialog
from gui.dialogs.PlotSettingsDialog import PlotSettingsDialog
from gui.dialogs.ProcedureDialog import ProcedureDialog
from gui.dialogs.ErrorDialog import ErrorDialog
from gui.dialogs.WarningDialog import WarningDialog

from gui.style import dark_stylesheet

from Device import Device
from Channel import Channel
from Procedure import Procedure, BasicProcedure, PidProcedure, TimerProcedure
from FileOps import load_from_csv


def query_server(com_pipe, server_url, debug=False):
    """ Sends info from RasPi server to communicator pipe """
    _keep_communicating = True
    _com_period = 5.0
    _device_dict_list = None
    poll_count = 0
    poll_time = timeit.default_timer()
    _paused = False

    while _keep_communicating:
        # Do the timing of this process:
        _thread_start_time = timeit.default_timer()
        if com_pipe.poll():
            _in_message = com_pipe.recv()
            if _in_message[0] == "com_period":
                _com_period = _in_message[1]
            elif _in_message[0] == "device_or_channel_changed":
                _device_dict_list = _in_message[1]
            elif _in_message[0] == "pause_query":
                _paused = not _paused

        if _device_dict_list is not None and _device_dict_list and not _paused:
            poll_count += 1
            _url = server_url + "device/query"
            _data = {'data': json.dumps(_device_dict_list)}

            try:
                _r = requests.post(_url, data=_data)
                timestamp = time.time()
                _response_code = _r.status_code
            except Exception as e:
                if debug:
                    print("Exception '{}' caught while communicating with RasPi server.".format(e))
                continue

            if _response_code == 200:
                _response = _r.text
                if debug:
                    print("The response was: {}".format(json.loads(_response)))
            else:
                if debug:
                    print("Response code was not 200: {}".format(_response_code))
                continue

            # if _response.strip() != r"{}" and "error" not in str(_response).lower():
            if _response.strip() != r"{}":
                parsed_response = json.loads(_response)
                parsed_response["timestamp"] = timestamp
                pipe_message = ["query_response", parsed_response]

                com_pipe.send(pipe_message)

        if poll_count == 20:
            duration = timeit.default_timer() - poll_time
            poll_time = timeit.default_timer()
            poll_count = 0
            polling_rate = 20.0 / duration

            pipe_message = ["polling_rate", polling_rate]
            com_pipe.send(pipe_message)

            if debug:
                print("Polling rate = {}".format(polling_rate))

        # Do the timing of this process:
        _sleepy_time = _com_period - timeit.default_timer() + _thread_start_time

        # if debug:
        # print("Sleeping for {} s".format(_sleepy_time))

        if _sleepy_time > 0.0:
            time.sleep(_sleepy_time)


class Communicator(QObject):
    """ Sends and recieves messages to and from the query process """

    sig_status = pyqtSignal(str)

    # gui update signals
    sig_poll_rate = pyqtSignal(float)
    sig_device_info = pyqtSignal(dict)

    def __init__(self, pipe):
        super().__init__()
        self._pipe = pipe
        self._terminate = False
        self._keep_communicating = True

        # need a queue for procedure actions
        self._message_queue = queue.Queue()

    def send_message(self, message):
        self._message_queue.put(message)

    @property
    def isRunning(self):
        return self._keep_communicating

    @isRunning.setter
    def isRunning(self, val):
        self._keep_communicating = val

    @property
    def pipe(self):
        return self._pipe

    @pyqtSlot()
    def communicate(self):
        while True:
            if self._keep_communicating:
                # listen to the pipe
                if self._pipe.poll():
                    gui_message = self._pipe.recv()
                    if gui_message[0] == "polling_rate":
                        self.sig_poll_rate.emit(gui_message[1])
                    elif gui_message[0] == "query_response":
                        self.sig_device_info.emit(gui_message[1])

                # if there is a message, send it
                if not self._message_queue.empty():
                    message = self._message_queue.get()
                    self._pipe.send(message)
                    self._message_queue.task_done()

                app.processEvents()

                if self._terminate:
                    break
            else:
                time.sleep(1.0)

            if self._terminate:
                self.sig_status.emit('Communicator terminating...')
                break

    def terminate(self):
        self.sig_status.emit('Communicator received terminate signal')
        self._terminate = True


class ControlSystem(object):

    def __init__(self, server_ip='127.0.0.1', server_port=80, debug=False):
        # --- Set up Qt UI and connect UI signals --- #
        self._window = MainWindow.MainWindow()

        self._window.ui.btnSave.triggered.connect(self.on_save_button)
        self._window.ui.btnSaveAs.triggered.connect(self.on_save_as_button)
        self._window.ui.btnLoad.triggered.connect(self.on_load_button)
        self._window._btnquit.triggered.connect(self.on_quit_button)

        self._window.ui.btnStartPause.clicked.connect(self.on_start_pause_click)
        self._window.ui.btnStop_2.clicked.connect(self.on_stop_click)
        self._window.ui.btnStop_2.setEnabled(False)
        self._window.ui.btnResetPinnedPlot.clicked.connect(self.reset_pinned_plot_callback)

        self._window.ui.btnSetupDevicePlots.clicked.connect(self.show_PlotChooseDialog)
        self._window.ui.btnAddProcedure.clicked.connect(self.show_ProcedureDialog)
        self._window._sig_entry_form_changed.connect(self.connect_device_channel_entry_form)

        # --- Plotting timer --- #
        self._plot_timer = QTimer()
        self._plot_timer.timeout.connect(self.update_value_displays)
        # self._plot_timer.start(25)

        # --- Initialize RasPi server --- #
        self.debug = debug
        self._server_url = 'http://{}:{}/'.format(server_ip, server_port)

        try:
            r = requests.get(self._server_url + 'initialize/')
            if r.status_code == 200:
                self._window.status_message(r.text)
            else:
                print('[Error initializing server] {}: {}'.format(r.status_code, r.text))
        except Exception as e:
            print('Exception was: {}'.format(e))
            exit()

        # --- Get devices connected to server --- #
        # r = requests.get(self._server_url + 'device/active')
        # if r.status_code == 200:
        #     devices = json.loads(r.text)
        #     for device_id, device_info in devices.items():
        #         self._window.status_message('Found {} with ID {} on port {}.'.format(
        #             device_info['identifier'],
        #             device_id,
        #             device_info['port']))
        # else:
        #     print('[Error getting devices] {}: {}'.format(r.status_code, r.text))
        #     sys.exit(0)

        # --- Set up communication pipes --- #
        self._keep_communicating = False
        self._retry_devices = False
        self._polling_rate = 30.0
        self._com_period = 1.0 / self._polling_rate

        # --- Set up data dictionaries and lists --- #
        self._devices = {}
        self._procedures = {}
        self._critical_procedures = {}
        self._plotted_channels = []
        self._locked_devices = []

        # --- Keep persistent communicator thread --- #
        self._com_thread = QThread()

        self._pinned_curve = self._window._pinnedplot.curve
        self._pinned_channel = None

        self._device_file_name = ''
        self._window.status_message('Initialization complete.')

    # ---- Server Communication ---- #
    def setup_communication_threads(self):
        """ Create gui/server pipe pair, start communicator """
        self._pipe_gui, pipe_server = Pipe()

        self._com_process = Process(target=query_server,
                                    args=(pipe_server, self._server_url, False,))

        self._keep_communicating = True

        self._communicator = Communicator(self._pipe_gui)
        self._communicator.moveToThread(self._com_thread)
        self._com_thread.started.connect(self._communicator.communicate)
        self._communicator.sig_status.connect(self.on_communicator_status)
        self._communicator.sig_poll_rate.connect(self.on_communicator_poll_rate)
        self._communicator.sig_device_info.connect(self.on_communicator_device_info)
        self._com_thread.start()

        # Tell the query process the current polling rate:
        pipe_message = ["com_period", self._com_period]
        self._communicator.send_message(pipe_message)

        # Get initial device/channel list and send to query process:
        self.device_or_channel_changed()

        # Start the query process:
        self._com_process.start()

        # this thread auto retries device connection every 30 seconds
        self._retry_devices = True
        self._retry_thread = threading.Thread(target=self.update_device_retry_labels, args=())
        self._retry_thread.start()

    def shutdown_communication_threads(self):
        self._keep_communicating = False
        try:
            self._com_process.terminate()
            self._com_process.join()
        except AttributeError:
            # if process doesn't exist
            pass

        try:
            self._communicator.terminate()
            self._com_thread.quit()
        except AttributeError:
            pass

        self._retry_devices = False
        try:
            del self._retry_thread
        except AttributeError:
            pass

    @pyqtSlot(str)
    def on_communicator_status(self, data: str):
        """ update status bar with thread message """
        self._window.status_message(data)

    @pyqtSlot(float)
    def on_communicator_poll_rate(self, data: float):
        """ update polling rate in GUI """
        self._window.set_polling_rate('{0:.2f}'.format(data))

    @pyqtSlot(dict)
    def on_communicator_device_info(self, data: dict):
        """ Read in message from the server, and update devices accordingly """
        parsed_response = data
        # print(parsed_response)

        for device_name, device in self._devices.items():
            device_id = device.device_id

            if device.locked or device_id not in parsed_response.keys():
                continue

            # if "ERROR" in parsed_response[device_id]:
            if any(resp in parsed_response[device_id] for resp in ("ERROR", "TIMEOUT")):
                device.lock(message=parsed_response[device_id])
                if device not in self._locked_devices:
                    self._locked_devices.append(device)
                continue

            if device in self._locked_devices:
                self._locked_devices.remove(device)
                device.overview_widget.hide_error_message()

            try:
                timestamp = parsed_response[device_id]['timestamp']
                device.polling_rate = parsed_response[device_id]['polling_rate']
            except KeyError:
                # did not get a valid response or dict might be empty
                continue

            for channel_name, value in parsed_response[device_id].items():
                # metadata the server sent back that doesn't contain channel values
                if channel_name in ['timestamp', 'polling_rate']:
                    continue

                channel = device.get_channel_by_name(channel_name)
                if channel is None:
                    device.lock(message='Could not find channel with name {}.'.format(channel_name))
                    if device not in self._locked_devices:
                        self._locked_devices.append(device)
                    continue

                # Scale value back to channel
                channel.value = value / channel.scaling
                self.update_stored_values(device_name, channel_name, timestamp)

                # try:
                #     self.log_data(channel, timestamp)
                # except Exception as e:
                #     if self.debug:
                #         print("Exception '{}' caught while trying to log data.".format(e))

    @pyqtSlot()
    def device_or_channel_changed(self):
        """ Sends a device changed request to the pipe """
        device_dict_list = [{
            'device_driver': device.driver,
            'device_id': device.device_id,
            'locked_by_server': False,
            'channel_ids': [name for name, mych in device.channels.items() if
                            mych.mode in ['read', 'both']],
            'precisions': [mych.precision for name, mych in device.channels.items() if
                           mych.mode in ['read', 'both']],
            'values': [None for name, mych in device.channels.items() if
                       mych.mode in ['read', 'both']],
            'data_types': [str(mych.data_type) for name, mych in device.channels.items() if
                           mych.mode in ['read', 'both']]
        }

            for device_name, device in self._devices.items()
            if not (device.locked or
                    len([name for name, mych in device.channels.items() if
                         mych.mode in ['read', 'both']]) == 0)]

        pipe_message = ["device_or_channel_changed", device_dict_list]

        try:
            self._communicator.send_message(pipe_message)
        except AttributeError:
            pass

    @pyqtSlot(Channel, object)
    def set_value_callback(self, channel, val):
        """ Creates a SET message to send to server """
        # values = None
        if channel.data_type == float:
            values = val * channel.scaling
        else:
            values = float(val)
        if self.debug:
            print('Set value callback was called with widget {}, '
                  'type {}, and scaled value {}.'.format(channel,
                                                         channel.data_type,
                                                         channel.value))

        _data = {'device_driver': channel.parent_device.driver,
                 'device_id': channel.parent_device.device_id,
                 'locked_by_server': False,
                 'channel_ids': [channel.name],
                 'precisions': [None],
                 'values': [values],
                 'data_types': [str(channel.data_type)]}

        # Create a new thread that sends the set command to the server and
        # waits for an answer.
        new_set_thread = threading.Thread(target=self.update_device_on_server, args=(_data,))
        new_set_thread.start()

    def update_device_retry_labels(self):
        while self._retry_devices:
            tr = 30
            for i in range(tr):
                tr -= 1
                for device in self._locked_devices:
                    device.overview_widget.set_retry_label(tr)
                time.sleep(1)
                if not self._retry_devices:
                    return

            for device in self._locked_devices:
                device.unlock()
            self.device_or_channel_changed()

    def update_device_on_server(self, _data):
        """ Sends POST request to RasPi server with new device/channel info """
        _url = self._server_url + "device/set"
        try:
            _data = {'data': json.dumps(_data)}
            _r = requests.post(_url, data=_data)

            if _r.status_code == 200:
                print("Sending set command to server successful, response was: {}".format(_r.text))
            else:
                print("Sending set command to server unsuccessful, response-code was: {}".format(_r.status_code))
        except Exception as e:
            if self.debug:
                print("Exception '{}' caught while communicating with RasPi server.".format(e))

    # ---- Internal variable modifiers ----

    def update_stored_values(self, device_name, channel_name, timestamp):
        """ Update the value deques for each channel """
        ch = self._devices[device_name].channels[channel_name]

        # zero values will crash log scale plots
        if ch.value == 0:
            ch.value = 1e-20

        if len(ch.x_values) > 0:
            # only append new data (i.e. if we are polling faster than this
            # device can respond, might receive same point twice)
            if ch.x_values[-1] != timestamp:
                ch.append_data(timestamp, ch.value)
        else:
            ch.append_data(timestamp, ch.value)

        # check basic procedures to see if we should activate them
        for name, procedure in self._procedures.items():
            if not isinstance(procedure, BasicProcedure):
                continue

            if not self._devices[device_name] in procedure.rule_devices():
                continue

            if procedure.should_perform_procedure():
                procedure.do_actions()

    @pyqtSlot(object)
    def connect_device_channel_entry_form(self, obj):
        """ Connects the new object's save and delete signals to the control system """
        try:
            obj.sig_entry_form_ok.disconnect()
        except TypeError:
            pass
        obj.sig_entry_form_ok.connect(self.on_device_channel_changed)

        try:
            obj.sig_delete.disconnect()
        except TypeError:
            pass
        obj.sig_delete.connect(self.on_device_channel_delete)

    @pyqtSlot(object)
    def on_device_channel_delete(self, obj):
        for procedure_name, procedure in self._procedures.items():
            used_devices, used_channels = procedure.devices_channels_used()
            if obj in used_devices | used_channels:
                self.show_ErrorDialog(
                    'Object is part of a procedure. Delete the procedure before deleting this object.')
                return

        ignored = self.show_WarningDialog('Delete objects at your own risk!')
        if ignored:
            if isinstance(obj, Device):
                del self._devices[obj.name]
            else:
                dev = self._devices[obj.parent_device.name]
                del dev.channels[obj.name]
                dev.update()

            self.update_gui_devices()
            self.device_or_channel_changed()
        print(obj)

    @pyqtSlot(object, dict)
    def on_device_channel_changed(self, obj, vals):
        """ Called when user presses Save Changes button on the settings page.
            Gets passed an old device/channel and new values, or a new
            device/channel, and no values. """

        # make sure the object is not part of a procedure
        for procedure_name, procedure in self._procedures.items():
            used_devices, used_channels = procedure.devices_channels_used()
            if obj in used_devices | used_channels:
                ignored = self.show_WarningDialog(
                    'Object is part of a procedure. Delete the procedure before editing this object.')
                if not ignored:
                    obj.reset_entry_form()
                    return
                else:
                    # if part of multiple procedures, we only want to show this once
                    break

        if isinstance(obj, Device):

            name_in_use = vals['name'] in self._devices.keys()
            id_in_use = vals['device_id'] in [x.device_id for _, x in self._devices.items()]
            editing_device = obj in [x for _, x in self._devices.items()]

            if editing_device:
                if name_in_use and vals['name'] != obj.name:
                    self.show_ErrorDialog('Device name already in use.')
                    obj.reset_entry_form()
                    # attempting to change device name to a name in-use
                    return

                if id_in_use and vals['device_id'] != obj.device_id:
                    self.show_ErrorDialog('Device ID already in use.')
                    obj.reset_entry_form()
                    # attempting to change device_id to an id in-use
                    return

            else:
                # adding a new device
                if name_in_use or id_in_use:
                    self.show_ErrorDialog('Device name already in use.')
                    obj.reset_entry_form()
                    # attempting to add a device with name or id in-use
                    return

            for attr, val in vals.items():
                if attr == 'name' and editing_device:
                    self._devices[val] = self._devices.pop(obj.name)
                setattr(obj, attr, val)

            if not editing_device:
                self.add_device(obj)

        elif isinstance(obj, Channel):

            editing_channel = obj in [x for _, x in obj.parent_device.channels.items()]
            name_in_use = vals['name'] in obj.parent_device.channels.keys()

            if editing_channel:
                if name_in_use and vals['name'] != obj.name:
                    self.show_ErrorDialog('Channel name already in use.')
                    obj.reset_entry_form()
                    return
            else:
                if name_in_use:
                    self.show_ErrorDialog('Channel name already in use.')
                    obj.reset_entry_form()
                    return

            for attr, val in vals.items():
                if attr == 'name' and editing_channel:
                    self._devices[obj.parent_device.name].channels[val] = \
                        self._devices[obj.parent_device.name].channels.pop(obj.name)
                setattr(obj, attr, val)

            if not editing_channel:
                obj.parent_device.add_channel(obj)
                self.add_channel(obj)

        self.device_or_channel_changed()
        self.update_gui_devices()

    def add_device(self, device):
        """ Adds a device to the control system """
        if device.name in self._devices.keys():
            self.show_ErrorDialog('Device with the same name already loaded.')
            return False

        device.parent = self

        # Add device to the list of devices in the control system
        self._devices[device.name] = device

        if device.overview_order == -1:
            device.overview_order = min([x.overview_order for _, x in self._devices.items()]) - 1
        device.initialize()

        for chname, ch in device.channels.items():
            self.add_channel(ch)

        # if the device gets disconnected and reconnected, need to send a message to the server
        device.sig_update_server.connect(self.device_or_channel_changed)

        device.reset_entry_form()

        # return true if successful
        return True

        """
        # Add corresponding channels to the hdf5 log.
        for channel_name, channel in device.channels().items():
            if channel.mode() == "read" or channel.mode() == "both":
                self._data_logger.add_channel(channel)


        # Add the device to the settings page tree.
        device_iter = self._settings_page_tree_store.insert(None, (len(self._settings_page_tree_store) - 1),
                                                            [device.label(), "Device", "edit_device", device.name(),
                                                             device.name()])
        """

    def add_channel(self, channel):
        if channel.parent_device is None:
            print('Attempt to add channel with no parent device to gui')
            return

        # channel.initialize()

        channel._set_signal.connect(self.set_value_callback)
        channel._pin_signal.connect(self.set_pinned_plot_callback)
        channel._settings_signal.connect(self.set_plot_settings_callback)

        channel.reset_entry_form()

        channel.parent_device.update()

    # ---- GUI ----

    def update_gui_devices(self):
        """ Main update function to be called when a device is changed """
        for name, device in self._devices.items():
            device.update()
        self._window.update_overview(self._devices)
        self._window.update_device_settings(self._devices)
        self._window.update_plots(self._devices, self._plotted_channels)
        self._window.update_procedures(self._procedures)

    @pyqtSlot()
    def on_start_pause_click(self):
        btn = self._window.ui.btnStartPause
        if btn.text() == 'Start Polling':
            self.setup_communication_threads()
            self._plot_timer.start(50)
            btn.setText('Pause Polling')
            self._window.ui.btnStop_2.setEnabled(True)
        elif btn.text() == 'Pause Polling':
            self._communicator.send_message('pause_query', )
            self._keep_communicating = False
            self._communicator.isRunning = False
            self._plot_timer.stop()
            btn.setText('Resume Polling')
        else:
            self._communicator.send_message('pause_query', )
            self._keep_communicating = True
            self._communicator.isRunning = True
            self._plot_timer.start(50)
            btn.setText('Pause Polling')

    @pyqtSlot()
    def on_stop_click(self):
        self._plot_timer.stop()
        self.shutdown_communication_threads()
        self._window.ui.btnStartPause.setText('Start Polling')
        self._window.ui.btnStop_2.setEnabled(False)
        for device in self._locked_devices:
            device.unlock()
            device.overview_widget.hide_error_message()
        self._locked_devices = []

        for device_name, device in self._devices.items():
            device.error_message = ''
            for channel_name, channel in device.channels.items():
                channel.clear_data()

        self.update_value_displays()
        # self._plotted_channels = {}
        # self.update_gui_devices()

    @pyqtSlot()
    def update_value_displays(self):
        """ This function is called by a QTimer to ensure the GUI has a chance
            to get input. Handles updating of 'read' values on the overview
            page, and redraws plots if applicable """

        # update the pinned plot
        if self._pinned_channel is not None:
            self._pinned_curve.setData(self._pinned_channel.x_values,
                                       self._pinned_channel.y_values,
                                       clear=True, _callsync='off')

        if self._window.current_tab == 'main':
            # update read values on overview page
            for name, device in self._devices.items():
                for chname, channel in device.channels.items():
                    if channel.read_widget is None:
                        continue

                    if channel.data_type in [int, float]:
                        fmt = '{:' + channel.displayformat + '}'
                        val = str(fmt.format(channel.value))
                        channel.read_widget.setText(val)

        elif self._window.current_tab == 'plots':
            # update the plotted channels
            for device_name, device in self._devices.items():
                # for channel_name, channel in device.channels.items():
                for channel in self._plotted_channels:
                    # pyqtgraph cant plot log of 0
                    channel._plot_curve.setData(channel.x_values, channel.y_values,
                                                clear=True, _callsync='off')

        app.processEvents()

    def reset_pinned_plot_callback(self):
        x = self._window._gbpinnedplot.layout().itemAt(0).widget()
        x.settings = self._pinned_channel.plot_settings

    def set_pinned_plot_callback(self, device, channel):
        """ Set the pinned plot when a user pressed the plot's pin button """
        # click button emits (device, channel)
        self._pinned_channel = channel

        # update plot settings
        x = self._window._gbpinnedplot.layout().itemAt(0).widget()
        x.setLabel('left', '{} [{}]'.format(channel.label, channel.unit))
        x.settings = channel.plot_settings
        self._window._gbpinnedplot.setTitle('{}.{}'.format(device.label, channel.label))

    @pyqtSlot(Channel)
    def set_plot_settings_callback(self, ch):
        """ Show the plot settings dialog when the user presses the plot's setting button """
        rng = ch._plot_widget.view_range
        ch._plot_settings['x']['min'] = rng[0][0]
        ch._plot_settings['x']['max'] = rng[0][1]
        ch._plot_settings['y']['min'] = rng[1][0]
        ch._plot_settings['y']['max'] = rng[1][1]

        _plotsettingsdialog = PlotSettingsDialog(ch)
        _plotsettingsdialog.exec_()

    @pyqtSlot()
    def on_quit_button(self):
        # shut down communication threads
        self.shutdown_communication_threads()
        self._window.close()

    # ---- dialogs ----

    def on_save_button(self):
        if self._device_file_name == '':
            fileName, _ = QFileDialog.getSaveFileName(self._window,
                                                      "Save Session as JSON", "", "Text Files (*.txt)")

            if fileName == '':
                return

            if fileName[-4:] != '.txt':
                fileName += '.txt'

            self._device_file_name = fileName

        with open(self._device_file_name, 'w') as f:
            devdict = {}
            for device_name, device in self._devices.items():
                devdict[device_name] = device.get_json()

            procdict = {}
            for proc_name, procedure in self._procedures.items():
                procdict[proc_name] = procedure.json

            winsettingsdict = self._window.current_settings()

            chpinname = None
            devpinname = None
            if self._pinned_channel is not None:
                chpinname = self._pinned_channel.name
                devpinname = self._pinned_channel.parent_device.name

            cssettingsdict = {
                'pinned-channel': chpinname,
                'pinned-device': devpinname,
                'plotted-channels': [(x.name, x.parent_device.name) for
                                     x in self._plotted_channels]
            }

            output = {
                'devices': devdict,
                'procedures': procdict,
                'window-settings': winsettingsdict,
                'control-system-settings': cssettingsdict,
            }

            json.dump(output, f, sort_keys=True, indent=4, separators=(', ', ': '))

        self._window.status_message('Saved session to {}.'.format(self._device_file_name))

    def on_save_as_button(self):
        fileName, _ = QFileDialog.getSaveFileName(self._window,
                                                  "Save Session as JSON", "", "Text Files (*.txt)")

        if fileName == '':
            return

        if fileName[-4:] != '.txt':
            fileName += '.txt'

        self._device_file_name = fileName

        self.on_save_button()

    @pyqtSlot()
    def on_load_button(self):
        successes = 0

        filename, _ = QFileDialog.getOpenFileName(self._window,
                                                  "Load session from JSON", "", "Text Files (*.txt)")

        if filename == '':
            return

        res = load_from_csv(filename)
        if res is None:
            self._window.status_message('Unable to read JSON.')
            return
        else:
            devices, procedures, winsettings, cssettings = res

        # Add devices and procedures
        for _, dev in devices.items():
            if self.add_device(dev):
                successes += 1

        for _, proc in procedures.items():
            self.add_procedure(proc)

        # Load control system settings
        self._window.apply_settings(winsettings)
        self.apply_settings(cssettings)

        if successes > 0:
            self._device_file_name = filename
            self.update_gui_devices()
            self._window.status_message('Loaded {} devices from JSON.'.format(successes))

    @pyqtSlot()
    def show_PlotChooseDialog(self):
        _plotchoosedialog = PlotChooseDialog(self._devices, self._plotted_channels)
        accept, chs = _plotchoosedialog.exec_()
        self._plotted_channels = chs
        self.update_gui_devices()

    def add_procedure(self, procedure):
        self._procedures[procedure.name] = procedure
        procedure.signal_edit.connect(self.edit_procedure)
        procedure.signal_delete.connect(self.delete_procedure)
        if isinstance(procedure, PidProcedure):
            procedure.set_signal.connect(self.set_value_callback)

        if isinstance(procedure, BasicProcedure):
            procedure.set_signal.connect(self.set_value_callback)

        procedure.initialize()

    def edit_procedure(self, proc):
        self.show_ProcedureDialog(False, proc=proc)

    def delete_procedure(self, proc):
        del self._procedures[proc.name]
        self._window.update_procedures(self._procedures)

    @pyqtSlot()
    @pyqtSlot(Procedure)
    def show_ProcedureDialog(self, btnbool, proc=None):
        _proceduredialog = ProcedureDialog(self._devices, self._procedures.keys(), proc)
        accept, rproc = _proceduredialog.exec_()

        if rproc is not None:
            if proc is not None:
                # if we edited a procedure delete the old version before adding the new one
                self.delete_procedure(proc)

            self.add_procedure(rproc)
            self._window.update_procedures(self._procedures)

    @pyqtSlot()
    def show_ErrorDialog(self, error_message='Error'):
        _errordialog = ErrorDialog(error_message)
        _errordialog.exec_()
        self.update_gui_devices()

    def show_WarningDialog(self, warning_message='Warning'):
        _warningdialog = WarningDialog(warning_message)
        userignored = _warningdialog.exec_()

        return userignored

    # ---- Other functions ---- #
    def apply_settings(self, settings):
        if settings == {}:
            return

        if settings['pinned-device'] is not None:
            dev = self._devices[settings['pinned-device']]
            ch = dev.channels[settings['pinned-channel']]
            self._pinned_channel = ch
            self.set_pinned_plot_callback(dev, ch)

        for item in settings['plotted-channels']:
            self._plotted_channels.append(self._devices[item[1]].channels[item[0]])

    def run(self):
        # self.setup_communication_threads()
        self.update_gui_devices()
        self._window.show()

# ---- End control system class ---- #


if __name__ == '__main__':

    app = QApplication([])
    app.setStyleSheet(dark_stylesheet())

    cs = ControlSystem(server_ip='10.77.0.2', server_port=5000, debug=False)
    #cs = ControlSystem(server_ip='127.0.0.1', server_port=5000, debug=False)

    # connect the closing event to the quit button procedure
    app.aboutToQuit.connect(cs.on_quit_button)

    # mydebug = False

    cs.run()
    sys.exit(app.exec_())
