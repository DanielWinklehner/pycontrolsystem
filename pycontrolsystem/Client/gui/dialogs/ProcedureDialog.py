#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Dialog for creating/editing procedures

import operator
# Noinspections necessary for PyCharm because installed PyQt5 module is just called 'pyqt'
# noinspection PyPackageRequirements
from PyQt5.QtWidgets import QDialog, QFrame, QLabel, QPushButton, QVBoxLayout, \
                            QHBoxLayout
# noinspection PyPackageRequirements
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from .ui_ProcedureDialog import Ui_ProcedureDialog
from ...Procedure import BasicProcedure, PidProcedure, TimerProcedure  # , Procedure
from ...gui.widgets.DeviceChannelComboBox import DeviceChannelComboBox


class ProcedureDialog(QDialog):

    def __init__(self, devices, procnames, proc=None):
        super().__init__()
        self.ui = Ui_ProcedureDialog()
        self.ui.setupUi(self)

        self._devdict = devices

        # maintain order of the list of devices
        self._devlist = [x for name, x in self._devdict.items()]
        self._actions = {}
        self._actioncontrols = {}
        self._procnames = procnames # need this to check that we don't add two procedures of the same name

        # if proc = None, assume this is for a new procedure
        # else, we are editing a procedure

        self._newproc = proc
        self._accepted = False

        self._currentTab = 'Basic'

        self.initialize()

    def initialize(self):
        self.ui.cbEvent.addItems(['Start up', 'Shut down', 
                                  'Emergency shut down'])

        # set up UI elements
        self.ui.cbActionBool.addItems(['On', 'Off'])
        self.ui.cbActionBool.hide()
        self.ui.cbRuleBool.addItems(['On', 'Off'])
        self.ui.cbRuleBool.hide()
        self.ui.lblRuleUnit.hide()
        self.ui.lblActionUnit.hide()
        self.ui.lblEmail.hide()
        self.ui.txtEmail.hide()
        self.ui.lblText.hide()
        self.ui.txtText.hide()
        self.ui.gbContact.hide()

        self.ui.btnDone.clicked.connect(self.on_done_click)
        self.ui.btnAddAction.clicked.connect(self.on_add_action_click)
        self.ui.chkEmail.stateChanged.connect(self.on_email_check_changed)
        self.ui.chkText.stateChanged.connect(self.on_text_check_changed)
        self.ui.rbValue.toggled.connect(self.on_value_toggled)
        self.ui.rbEvent.toggled.connect(self.on_event_toggled)

        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        self._vboxActions = QVBoxLayout()
        self._vboxActions.addStretch()
        self.ui.fmActions.setLayout(self._vboxActions)

        # Fill comboboxes with devices/channels
        devnamelist = [x.label for x in self._devlist]
        self._cbDevChRule = DeviceChannelComboBox(self._devdict)
        self._cbDevChAction = DeviceChannelComboBox(self._devdict)

        self.ui.hlayoutRule.insertWidget(1, self._cbDevChRule)
        self.ui.hlayoutAction.insertWidget(1, self._cbDevChAction)

        self.ui.cbRuleCompare.addItems(['<', '>', '=', '<=', '>='])
        self._cbDevChRule.channel_changed_signal.connect(self.on_rule_channel_cb_changed)
        self._cbDevChAction.channel_changed_signal.connect(self.on_action_channel_cb_changed)

        # pid device/channel selectors -- channels must be floats
        self._cbDevChPidRead = DeviceChannelComboBox(
                self._devdict, channel_params = {'mode': ('read','both'), 
                                                 'data_type': (float,)
                                                 })

        self._cbDevChPidWrite = DeviceChannelComboBox(
                self._devdict, channel_params = {'mode': ('write','both'), 
                                                 'data_type': (float,)
                                                 })

        self.ui.gridPid.addWidget(self._cbDevChPidRead, 0, 1)
        self.ui.gridPid.addWidget(self._cbDevChPidWrite, 1, 1)

        self._cbDevChPidWrite.channel_changed_signal.connect(
                self.on_pid_write_channel_cb_changed)

        # timer device/channel selectors
        self._cbDevChTimerStart = DeviceChannelComboBox(
                self._devdict, channel_params = {'mode': ('read','both')})

        self._cbDevChTimerStop = DeviceChannelComboBox(
                self._devdict, channel_params = {'mode': ('read','both')})

        self.ui.gbTimerStart.layout().addWidget(self._cbDevChTimerStart, 0, 1)
        self.ui.gbTimerStop.layout().addWidget(self._cbDevChTimerStop, 0, 1)

        self._cbDevChTimerStart.channel_changed_signal.connect(
                self.on_timer_start_channel_cb_changed)
        self._cbDevChTimerStop.channel_changed_signal.connect(
                self.on_timer_stop_channel_cb_changed)

        if self._newproc != None:
            self.ui.txtProcedureName.setText(self._newproc.name)
            if isinstance(self._newproc, BasicProcedure):
                self.ui.tab_2.setParent(None)
                self.ui.tab_3.setParent(None)
                self.initialize_basic_procedure()
            elif isinstance(self._newproc, PidProcedure):
                self.ui.tab.setParent(None)
                self.ui.tab_3.setParent(None)
                self.initialize_pid_procedure()
            elif isinstance(self._newproc, TimerProcedure):
                self.ui.tab.setParent(None)
                self.ui.tab_2.setParent(None)
                self.initialize_timer_procedure()

    def initialize_basic_procedure(self):
        for idx, rule in self._newproc.rules.items():
            # TODO: currently only works with 1 rule
            self._cbDevChRule.select(rule['channel'])

            # Set comparison operator and value
            if rule['channel'].data_type != bool:
                self.ui.txtRuleVal.setText(str(rule['value']))
                if rule['comp'] == operator.lt:
                    self.ui.cbRuleCompare.setCurrentIndex(0)
                elif rule['comp'] == operator.gt:
                    self.ui.cbRuleCompare.setCurrentIndex(1)
                elif rule['comp'] == operator.eq:
                    self.ui.cbRuleCompare.setCurrentIndex(2)
                elif rule['comp'] == operator.le:
                    self.ui.cbRuleCompare.setCurrentIndex(3)
                elif rule['comp'] == operator.ge:
                    self.ui.cbRuleCompare.setCurrentIndex(4)

            else:
                # since we already changed the index to a channel of type bool,
                # the bool combo box should be visible
                if rule['value']:
                    self.ui.cbRuleBool.setCurrentIndex(0)
                else:
                    self.ui.cbRuleBool.setCurrentIndex(1)

        # add the actions
        for idx, action in self._newproc.actions.items():
            self._cbDevChAction.select(action['channel'])

            self.ui.txtDelay.setText(str(action['delay']))

            # set the data text
            if action['channel'].data_type != bool:
                self.ui.txtActionVal.setText(str(action['value']))
            else:
                if action['value']:
                    self.ui.cbActionBool.setCurrentIndex(0)
                else:
                    self.ui.cbActionBool.setCurrentIndex(1)

            self.on_add_action_click()

        if self._newproc.critical:
            self.ui.chkCritical.toggle()

        if self._newproc.email != '':
            self.ui.chkEmail.toggle()
            self.ui.gbContact.show()
            self.ui.lblEmail.show()
            self.ui.txtEmail.show()
            self.ui.txtEmail.setText(self._newproc.email)

        if self._newproc.sms != '':
            self.ui.chkText.toggle()
            self.ui.gbContact.show()
            self.ui.lblText.show()
            self.ui.txtText.show()
            self.ui.txtText.setText(self._newproc.sms)

    def initialize_pid_procedure(self):
        # Get write device/channel
        self._cbDevChPidWrite.select(self._newproc._write_channel)
        self._cbDevChPidRead.select(self._newproc._pid.channel)

        self.ui.txtTarget.setText(str(self._newproc._pid.target))
        self.ui.txtP.setText(str(self._newproc._pid.coeffs[0]))
        self.ui.txtI.setText(str(self._newproc._pid.coeffs[1]))
        self.ui.txtD.setText(str(self._newproc._pid.coeffs[2]))
        self.ui.txtdt.setText(str(self._newproc._pid.dt))

        self.ui.txtAverage.setText(str(self._newproc._pid.ma))
        self.ui.txtWarmup.setText(str(self._newproc._pid.warmup))
        self.ui.txtOffset.setText(str(self._newproc._pid.offset))
        self.ui.lblUnit.setText(self._newproc._write_channel.unit)

        self._currentTab = 'PID'
        self.ui.gbOptions.setEnabled(False)
        self.ui.gbNotify.setEnabled(False)

    def initialize_timer_procedure(self):
        # Get write device/channel
        self._cbDevChTimerStart.select(self._newproc._timer.start_channel)
        self._cbDevChTimerStop.select(self._newproc._timer.stop_channel)

        self.ui.txtTimerStart.setText(str(self._newproc._timer.start_value))
        self.ui.txtTimerStop.setText(str(self._newproc._timer.stop_value))

        if self._newproc._timer.start_comp_str == 'less':
            self.ui.cbTimerStartComp.setCurrentIndex(1)
        if self._newproc._timer.stop_comp_str == 'less':
            self.ui.cbTimerStopComp.setCurrentIndex(1)

        self.ui.txtTimerMinTime.setText(str(self._newproc._timer.min_time))
        if self._newproc._timer.continuous:
            self.ui.chkTimerContinuous.toggle()

        self._currentTab = 'Timer'
        self.ui.gbOptions.setEnabled(False)
        self.ui.gbNotify.setEnabled(False)

    def on_tab_changed(self, idx):
        if idx == 1:
            self._currentTab = 'PID'
            self.ui.gbOptions.setEnabled(False)
            self.ui.gbNotify.setEnabled(False)
        elif idx == 2:
            self._currentTab = 'Timer'
            self.ui.gbOptions.setEnabled(False)
            self.ui.gbNotify.setEnabled(False)
        elif idx == 0:
            self._currentTab = 'Basic'
            self.ui.gbOptions.setEnabled(True)
            self.ui.gbNotify.setEnabled(True)

    def on_value_toggled(self, isChecked):
        self._cbDevChRule.setEnabled(isChecked)
        self.ui.cbRuleCompare.setEnabled(isChecked)
        self.ui.cbRuleBool.setEnabled(isChecked)
        self.ui.txtRuleVal.setEnabled(isChecked)

    def on_event_toggled(self, isChecked):
        self.ui.cbEvent.setEnabled(isChecked)

    def on_add_action_click(self):
        channel = self._cbDevChAction.selected_channel

        if channel is None:
            return

        try:
            delay = float(self.ui.txtDelay.text())
        except ValueError:
            print('Error: Bad delay input')
            return

        if channel.data_type != bool:
            try:
                value = channel.data_type(self.ui.txtActionVal.text())
            except ValueError:
                print('Error: Bad input')
                return

            if value > channel.upper_limit or value < channel.lower_limit:
                print('Error: Exceeded channel limits')
                return
        else:
            if self.ui.cbActionBool.currentText() == 'On':
                value = True
            else:
                value = False
            
        index = len(self._actions)

        fm = QFrame()
        
        vbox = QVBoxLayout()
        lblDevCh = QLabel(channel.parent_device.label + '.' + channel.label)
        if channel.data_type != bool:
            lblSetVal = QLabel('Set value: {} {}, delay: {} seconds'.format(
                str(value), channel.unit, delay))
        else:
            if value:
                lblSetVal = QLabel('Set value: On, delay: {} seconds'.format(delay))
            else:
                lblSetVal = QLabel('Set value: Off, delay: {} seconds'.format(delay))

        vbox.addWidget(lblDevCh)
        vbox.addWidget(lblSetVal)

        btnDel = QPushButtonX('Delete', index)
        btnDel.clickedX.connect(self.on_delete_action_click)

        hbox = QHBoxLayout()
        lblNum = QLabel(str(index + 1) + '. ')
        hbox.addWidget(lblNum)
        hbox.addLayout(vbox)
        hbox.addStretch()
        hbox.addWidget(btnDel)

        fm.setLayout(hbox)

        self._vboxActions.insertWidget(0, fm)

        self.ui.txtActionVal.setText('')
        self.ui.txtDelay.setText('0.0')
        self._cbDevChAction.select(None)
        self.ui.cbActionBool.hide()
        self.ui.txtActionVal.show()

        self._actions[index] = {'device' : channel.parent_device, 
                                'channel' : channel, 'value' : value,
                                'delay': delay}
        self._actioncontrols[index] = {'button' : btnDel, 'frame' : fm, 
                                       'label' : lblNum, 'layout' : hbox}

    def on_delete_action_click(self, index):
        del self._actions[index]
        self._actioncontrols[index]['frame'].deleteLater()
        del self._actioncontrols[index]

        # fix numbering of actions. Shift all actions above the deleted one by 1
        # e.g. in list of 0,1,2,3 -> Delete 1 -> shift 2 to 1, 3 to 2
        newactions = {}
        newactioncontrols = {}
        
        actionlist = [action for idx, action in sorted(self._actions.items(), key=lambda t: int(t[0]))]
        actioncontrollist = [controls for idx, controls in sorted(self._actioncontrols.items(), key=lambda t: int(t[0]))]
        
        # get rid of the pesky old-indexed buttons
        for control in actioncontrollist:
            control['button'].deleteLater()
            del control['button']

        for i, action in enumerate(actionlist):
            # fill shifted lists
            newactions[i] = action
            
            controls = actioncontrollist[i]
            controls['label'].setText(str(i + 1) + '. ')
            btnDel = QPushButtonX('Delete', i)
            btnDel.clickedX.connect(self.on_delete_action_click)
            controls['button'] = btnDel
            controls['layout'].addWidget(btnDel)

            newactioncontrols[i] = controls

        self._actions = newactions
        self._actioncontrols = newactioncontrols

    def on_timer_start_channel_cb_changed(self, channel):
        if channel is not None:
            self.ui.lblTimerStartUnit.setText(channel.unit)
        else:
            self.ui.lblTimerStartUnit.setText('')

    def on_timer_stop_channel_cb_changed(self, channel):
        if channel is not None:
            self.ui.lblTimerStopUnit.setText(channel.unit)
        else:
            self.ui.lblTimerStopUnit.setText('')

    def on_pid_write_channel_cb_changed(self, channel):
        if channel is not None:
            self.ui.lblUnit.setText(channel.unit)
        else:
            self.ui.lblUnit.setText('')

    def on_rule_channel_cb_changed(self, channel):
        if channel is not None:
            self.ui.lblRuleUnit.setText(channel.unit)
            if channel.data_type == bool:
                # switch text field for combobox
                self.ui.cbRuleBool.show()
                self.ui.txtRuleVal.hide()
                self.ui.lblRuleUnit.hide()
                self.ui.cbRuleCompare.hide()
            else:
                # switch combobox for text field
                self.ui.cbRuleBool.hide()
                self.ui.txtRuleVal.show()
                self.ui.lblRuleUnit.show()
                self.ui.cbRuleCompare.show()
        else:
            self.ui.cbRuleBool.hide()
            self.ui.txtRuleVal.show()
            self.ui.cbRuleCompare.show()

    def on_action_channel_cb_changed(self, channel):
        if channel is not None:
            self.ui.lblActionUnit.setText(channel.unit)
            if channel.data_type == bool:
                # switch text field for combobox
                self.ui.cbActionBool.show()
                self.ui.lblActionUnit.hide()
                self.ui.txtActionVal.hide()
            else:
                # switch combobox for test field
                self.ui.cbActionBool.hide()
                self.ui.lblActionUnit.show()
                self.ui.txtActionVal.show()
        else:
            # switch combobox for test field
            self.ui.cbActionBool.hide()
            self.ui.txtActionVal.show()

    def on_email_check_changed(self, isChecked):
        if isChecked:
            self.ui.gbContact.show()
            self.ui.txtEmail.show()
            self.ui.lblEmail.show()
        else:
            self.ui.txtEmail.hide()
            self.ui.lblEmail.hide()
            self.ui.txtEmail.setText('')
            if not self.ui.chkText.isChecked():
                self.ui.gbContact.hide()

    def on_text_check_changed(self, isChecked):
        if isChecked:
            self.ui.gbContact.show()
            self.ui.txtText.show()
            self.ui.lblText.show()
        else:
            self.ui.txtText.hide()
            self.ui.lblText.hide()
            self.ui.txtText.setText('')
            if not self.ui.chkEmail.isChecked():
                self.ui.gbContact.hide()

    def validate_basic_procedure(self):
        channel = self._cbDevChRule.selected_channel
        if channel is None:
            return False

        if channel.data_type != bool:
            try:
                value = channel.data_type(self.ui.txtRuleVal.text())
            except:
                print('Error: Bad value for Rule')
                return False
        else:
            if self.ui.cbRuleBool.currentText() == 'On':
                value = True
            else:
                value = False

        if channel.data_type != bool:
            comptext = self.ui.cbRuleCompare.currentText()
            if comptext == '=':
                comp = operator.eq
            elif comptext == '>':
                comp = operator.gt
            elif comptext == '<':
                comp = operator.lt
            elif comptext == '>=':
                comp = operator.ge
            elif comptext == '<=':
                comp = operator.le
        else:
            comp = operator.eq


        rule = {'1' : {'device' : channel.parent_device, 
                       'channel' : channel, 'value' : value,'comp' : comp}}

        self._newproc = BasicProcedure(self.ui.txtProcedureName.text(), 
                                       rule, self._actions, 
                                       self.ui.chkCritical.isChecked(), 
                                       self.ui.txtEmail.text(), 
                                       self.ui.txtText.text())

        print('Created new procedure:')
        print(self._newproc)

        return True
    
    def validate_pid_procedure(self):
        readchannel = self._cbDevChPidRead.selected_channel
        writechannel = self._cbDevChPidWrite.selected_channel

        if readchannel is None or writechannel is None:
            print('Channel not selected')
            return False

        try:
            target = float(self.ui.txtTarget.text())
            p = float(self.ui.txtP.text())
            i = float(self.ui.txtI.text())
            d = float(self.ui.txtD.text())
            dt = float(self.ui.txtdt.text())
            ma = int(self.ui.txtAverage.text())
            warmup = int(self.ui.txtWarmup.text())
            offset = float(self.ui.txtOffset.text())
        except:
            print('bad values entered')
            return False

        self._newproc = PidProcedure(self.ui.txtProcedureName.text(),
                                     readchannel, writechannel,
                                     target, [p,i,d], dt,
                                     ma, warmup, offset)

        return True

    def validate_timer_procedure(self):
        startchannel = self._cbDevChTimerStart.selected_channel
        stopchannel = self._cbDevChTimerStop.selected_channel

        if startchannel is None or stopchannel is None:
            print('Channel not selected')
            return False

        try:
            start_value = float(self.ui.txtTimerStart.text())
            stop_value = float(self.ui.txtTimerStop.text())
            min_time = float(self.ui.txtTimerMinTime.text())
        except:
            print('bad values entered')
            return False

        if self.ui.cbTimerStartComp.currentIndex() == 0:
            start_comp = operator.gt
        else:
            start_comp = operator.lt

        if self.ui.cbTimerStopComp.currentIndex() == 0:
            stop_comp = operator.gt
        else:
            stop_comp = operator.lt

        self._newproc = TimerProcedure(self.ui.txtProcedureName.text(),
                                       startchannel, start_value, start_comp,
                                       stopchannel, stop_value, stop_comp,
                                       min_time, self.ui.chkTimerContinuous.isChecked())

        return True

    def on_done_click(self):
        if self._newproc == None and self.ui.txtProcedureName.text() in self._procnames:
            # if self._newproc is not None, then we are editing a procedure, so ok to overwrite
            print('Error: Procedure name already in use')
            return

        validated = False

        if self._currentTab == 'Basic':
            validated = self.validate_basic_procedure()
        elif self._currentTab == 'PID':
            validated = self.validate_pid_procedure()
        elif self._currentTab == 'Timer':
            validated = self.validate_timer_procedure()

        if validated:
            self._accepted = True
            self.accept()

    def exec_(self):
        super(ProcedureDialog, self).exec_()
        return self._accepted, self._newproc

class QPushButtonX(QPushButton):
    """ QPushButton which returns its index """
    clickedX = pyqtSignal(int)

    def __init__(self, text, index):
        super().__init__()
        self._index = index
        self.setText(text)
        self.clicked.connect(self.on_clicked)

    @pyqtSlot()
    def on_clicked(self):
        self.clickedX.emit(self._index)
