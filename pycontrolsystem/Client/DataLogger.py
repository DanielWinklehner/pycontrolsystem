import h5py
import numpy as np
import time
import os


class DataLogger(object):
    def __init__(self, filename):
        self._h5fn = filename
        self._h5file = None
        self._data_set = {}
        self._main_group = None

    def initialize(self):
        if not os.path.exists(os.path.dirname(self._h5fn)):
            os.makedirs(os.path.dirname(self._h5fn))
        self._h5file = h5py.File(self._h5fn, "w")
        self._main_group = self._h5file.create_group("mist1_control_system")

    def add_device(self, dev_name):
        if dev_name not in self._main_group.keys():
            self._main_group.create_group(dev_name)

    def add_channel(self, dev_name, ch_name):

        self.add_device(dev_name)

        if ch_name not in self._main_group[dev_name].keys():
            dset = self._main_group[dev_name].create_dataset(ch_name, (1, 2), maxshape=(None, 2),
                                                             dtype=float, compression="gzip")
            self._data_set[dset.name] = dset

    def log_value(self, dev_name, ch_name, ch_value, timestamp):

        self.add_channel(dev_name, ch_name)

        if ch_value is not None:
            dataset_name = "{}/{}/{}".format(self._main_group.name, dev_name, ch_name)
            dset = self._data_set[dataset_name]

            dset.resize((len(dset) + 1, 2))

            a = (timestamp, ch_value)
            dset[len(dset) - 1] = a

            self._h5file.flush()
