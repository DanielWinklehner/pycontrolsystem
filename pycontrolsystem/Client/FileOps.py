#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Thomas Wester <twester@mit.edu>
#
# Loading/saving functions for control system

import json
import operator

from Device import Device
from Channel import Channel
from Procedure import BasicProcedure, PidProcedure, TimerProcedure


def str_to_comp(compstr):
    """" Translate an operator string to an operator object """
    if compstr == 'equal':
        return operator.eq

    if compstr == 'less':
        return operator.lt

    if compstr == 'greater':
        return operator.gt

    if compstr == 'greatereq':
        return operator.ge

    if compstr == 'lesseq':
        return operator.le

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
        elif proc_type == 'basic':
            rules = {}
            actions = {}
            for idx, rule in filtered_params['rules'].items():
                rules[idx] = {'comp': str_to_comp(rule['comp']),
                              'device': devices[rule['rule_device']],
                              'channel': devices[rule['rule_device']].channels[rule['rule_channel']],
                              'value': rule['value']
                              }

            for idx, action in filtered_params['actions'].items():
                actions[idx] = {'device': devices[action['action_device']],
                                'channel': devices[action['action_device']].channels[action['action_channel']],
                                'delay': action['action_delay'],
                                'value': action['action_value'],
                               }

            filtered_params['rules'] = rules
            filtered_params['actions'] = actions

            proc = BasicProcedure(**filtered_params)

        procedures[proc.name] = proc

    return devices, procedures, winsettings, cssettings
