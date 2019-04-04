# noinspection PyPackageRequirements
from PyQt5.QtWidgets import QDialog
from .ui_SlackDialog import Ui_SlackDialog
from slackclient import SlackClient


class SlackDialog(QDialog):
    def __init__(self, token=None, channel=None):
        super().__init__()
        self.ui = Ui_SlackDialog()
        self.ui.setupUi(self)

        self._sc = None
        self._slack_token = token
        self._token_ok = False
        self._channel_id = channel
        self._ret_data = None

        if self._slack_token is not None:
            self.ui.lineEditToken.setText(self._slack_token)
        if self._channel_id is not None:
            self.ui.lineEditChannel.setText(self._channel_id)

        # Cave: Connect after setting the text boxes, otherwise channel will be set to None
        self.ui.btnTestToken.clicked.connect(self.test_slack_token)
        self.ui.btnTestChannel.clicked.connect(self.test_slack_channel)
        self.ui.lineEditToken.textChanged.connect(self.on_line_edit_token_changed)
        self.ui.lineEditChannel.textChanged.connect(self.on_line_edit_channel_changed)

        self._ok_cancel = 0

    def on_line_edit_token_changed(self, ):

        self._sc = None
        self._slack_token = None
        self._token_ok = False
        self._channel_id = None

    def on_line_edit_channel_changed(self, ):

        self._channel_id = None

    def test_slack_token(self):

        self._slack_token = self.ui.lineEditToken.text()
        self._sc = SlackClient(self._slack_token)
        test_data = self._sc.api_call("api.test")

        if test_data['ok']:
            labeltext = "Testing Slack communication: Success!"
            self._token_ok = True
        else:
            labeltext = "Testing Slack communication: Fail!\nError: {}".format(test_data['error'])
            self.on_line_edit_token_changed()  # Reset stored values

        self.ui.label_success.setText(labeltext)

    def test_slack_channel(self):

        if self._sc is None:
            self.test_slack_token()

        if self._token_ok:
            channel_name_id = self.ui.lineEditChannel.text()  # Could be either name or ID

            test_data = self._sc.api_call("channels.list")

            self._channel_id = None
            for _channel in test_data["channels"]:
                if _channel["name"] == channel_name_id or _channel["id"] == channel_name_id:
                    self._channel_id = _channel["id"]

            test_data = self._sc.api_call("channels.info", channel=self._channel_id)

            if test_data['ok']:
                labeltext = "Testing Slack Channel: Success!\n" \
                            "Channel ID: {}\n" \
                            "Channel Name: {}".format(self._channel_id, test_data['channel']['name'])
            else:
                labeltext = "Testing Slack Channel: Fail!\nError: {}".format(test_data['error'])
                self._channel_id = None

            self.ui.label_success.setText(labeltext)

    def accept(self):

        self._ok_cancel = 1
        self._ret_data = None

        if self._channel_id is None:

            self.test_slack_channel()

        if self._channel_id is not None:

            self._ret_data = {"token": self._slack_token,
                              "channel_id": self._channel_id}

        super(SlackDialog, self).accept()

    def reject(self):

        self._ok_cancel = 0
        self._ret_data = None

        super(SlackDialog, self).reject()

    def exec_(self):

        super(SlackDialog, self).exec_()

        return self._ok_cancel, self._ret_data
