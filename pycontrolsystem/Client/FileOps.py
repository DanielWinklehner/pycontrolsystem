#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Thomas Wester <twester@mit.edu>
#
# Loading/saving functions for control system

import json
import operator

from lib.Device import Device
from lib.Channel import Channel
from lib.Procedure import PidProcedure, TimerProcedure 

def load_from_csv(filename=''):

    if filename == '':
        print('no filename')
        return None

    with open(filename, 'r') as f:
        try:
            data = json.loads(f.read())
        except:
            print('unable to read json')
            return None

    devicedata = data['devices']
    proceduredata = data['procedures']
    winsettings = data['window-settings']
    cssettings = data['control-system-settings']

    devices = {}
    procedures = {}

    # Load devices
    for device_name, device_data in devicedata.items():
        filtered_params = {}
        for key, value in device_data.items():
            if not key == "channels":
                filtered_params[key] = value

        device = Device(**filtered_params)

        for channel_name, channel_data in device_data['channels'].items():
            data_type_str = channel_data['data_type']
            channel_data['data_type'] = eval(data_type_str.split("'")[1])

            ch = Channel(**channel_data)
            device.add_channel(ch)

        devices[device.name] = device

    # Load procedures
    for proc_name, proc_data in proceduredata.items():
        filtered_params = {}
        proc_type = ''
        for key, value in proc_data.items():
            if key == 'type':
                proc_type = value
            elif key in ['write-channel', 'write-device', 'read-channel', 'read-device']:
                pass
            elif key in ['start-channel', 'start-device', 'stop-channel', 'stop-device']:
                pass
            elif key in ['stop_comp', 'start_comp']:
                filtered_params[key] = operator.gt if value == 'greater' else operator.lt
            else:
                filtered_params[key] = value

        if proc_type == 'pid':
            filtered_params['read_channel'] = \
                devices[proc_data['read-device']].channels[proc_data['read-channel']]
            filtered_params['write_channel'] = \
                devices[proc_data['write-device']].channels[proc_data['write-channel']]
            proc = PidProcedure(**filtered_params)
        elif proc_type == 'timer':
            filtered_params['start_channel'] = \
                devices[proc_data['start-device']].channels[proc_data['start-channel']]
            filtered_params['stop_channel'] = \
                devices[proc_data['stop-device']].channels[proc_data['stop-channel']]
            proc = TimerProcedure(**filtered_params)

        procedures[proc.name] = proc

    return (devices, procedures, winsettings, cssettings)
