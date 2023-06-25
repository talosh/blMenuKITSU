import os
import sys
import base64
import time
from PyQt5 import QtGui, QtWidgets, QtCore

from .kitsu import appKitsuConnector
from .baselight import appBaselightConnector

from pprint import pprint, pformat

class FramelessWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self._old_pos = None

    def mousePressEvent(self, event):
        self._old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self._old_pos = None

    def mouseMoveEvent(self, event):
        if self._old_pos:
            delta = event.pos() - self._old_pos
            self.move(self.pos() + delta)

            
class blMenuKITSU(FramelessWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.framework = kwargs.get('framework')
        self.prefs = self.framework.prefs
        self.kitsu_connector = appKitsuConnector(self.framework)
        if self.kitsu_connector.gazu_client:
            self.kitsu_status = 'Connected'
        else:
            self.kitsu_status = 'Disconnected'

        self.user = None
        self.user_name = None

        self.kitsu_host = self.prefs.get('kitsu_host', 'http://localhost/api/')
        self.kitsu_user = self.prefs.get('kitsu_user', 'user@host')
        self.kitsu_pass = ''
        encoded_kitsu_pass = self.prefs.get('kitsu_pass', '')
        if encoded_kitsu_pass:
            self.kitsu_pass = base64.b64decode(encoded_kitsu_pass).decode("utf-8")

        self.bl_connector = appBaselightConnector(self.framework)
        self.flapi_host = self.prefs.get('flapi_host', 'localhost')
        self.flapi_key = self.prefs.get('flapi_key', '')
        self.initUI()

        self.kitsu_connect_btn.click()
        self.flapi_connect_btn.click()

    def initUI(self):
        self.main_window()
        self.setStyleSheet("background-color: rgb(49, 49, 49);")
        self.show()

    def main_window(self):

        self.kitsu_host_text = self.kitsu_host
        self.kitsu_user_text = self.kitsu_user
        self.kitsu_pass_text = self.kitsu_pass
        self.flapi_host_text = self.flapi_host
        self.flapi_key_text = self.flapi_key

        def txt_KitsuHost_textChanged():
            self.kitsu_host_text = txt_KitsuHost.text()
            # storage_root_paths.setText(calculate_project_path())

        def txt_KitsuUser_textChanged():
            self.kitsu_user_text = txt_KitsuUser.text()

        def txt_KitsuPass_textChanged():
            self.kitsu_pass_text = txt_KitsuPass.text()

        def txt_KitsuConnect_Clicked():
            if not self.kitsu_connector.gazu_client:
                lbl_KitsuStatus.setText('Connecting...')
                self.prefs['kitsu_host'] = self.kitsu_host_text
                self.prefs['kitsu_user'] = self.kitsu_user_text
                self.prefs['kitsu_pass'] = base64.b64encode(self.kitsu_pass_text.encode("utf-8")).decode("utf-8")
                self.framework.save_prefs()
                self.kitsu_connector.get_user(msg = True)
                if self.kitsu_connector.gazu_client:
                    self.kitsu_status = 'Connected'
                    lbl_KitsuStatus.setText(self.kitsu_status)
                    kitsu_connect_btn.setText('Disconnect')
                else:
                    self.kitsu_status = 'Disconnected'
                    kitsu_connect_btn.setText('Connect')
                    lbl_KitsuStatus.setText(self.kitsu_status)
            else:
                self.kitsu_connector.gazu_client = None
                self.kitsu_connector.user = None
                self.kitsu_connector.user_name = None
                self.kitsu_status = 'Disconnected'
                lbl_KitsuStatus.setText(self.kitsu_status)
                kitsu_connect_btn.setText('Connect')

        def txt_FlapiHost_textChanged():
            self.flapi_host_text = txt_KitsuPass.text()

        def txt_FlapiKey_textChanged():
            self.flapi_key_text = txt_FlapiKey.text()

        def txt_FlapiConnect_Clicked():
            flapi_connect_btn.setText('Disconnect')

        def toggle_kitsu_password_visibility():
            if txt_KitsuPass.echoMode() == QtWidgets.QLineEdit.Password:
                txt_KitsuPass.setEchoMode(QtWidgets.QLineEdit.Normal)
            else:
                txt_KitsuPass.setEchoMode(QtWidgets.QLineEdit.Password)

        def toggle_flapikey_visibility():
            if txt_FlapiKey.echoMode() == QtWidgets.QLineEdit.Password:
                txt_FlapiKey.setEchoMode(QtWidgets.QLineEdit.Normal)
            else:
                txt_FlapiKey.setEchoMode(QtWidgets.QLineEdit.Password)

        # window = QtWidgets.QWidget()
        window = self
        window.setWindowTitle(self.framework.app_name)
        window.setStyleSheet('background-color: #313131')
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.setMinimumSize(450, 180)
        screen_res = QtWidgets.QDesktopWidget().screenGeometry()
        window.move((screen_res.width()/2)-150, (screen_res.height() / 2)-180)
        # window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        vbox1 = QtWidgets.QVBoxLayout()

        lbl_KitsuLogin = QtWidgets.QLabel('Kitsu Server Login: ', window)
        lbl_KitsuLogin.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_KitsuLogin.setFixedHeight(28)
        lbl_KitsuLogin.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        vbox1.addWidget(lbl_KitsuLogin)

        hbox1 = QtWidgets.QHBoxLayout()

        lbl_Host = QtWidgets.QLabel('Server: ', window)
        lbl_Host.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_Host.setFixedSize(108, 28)
        lbl_Host.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_KitsuHost = QtWidgets.QLineEdit(self.kitsu_host, window)
        txt_KitsuHost.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_KitsuHost.setMinimumSize(280, 28)
        # txt_KitsuHost.move(128,0)
        txt_KitsuHost.setStyleSheet(
            'QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454;}'
            )
        txt_KitsuHost.textChanged.connect(txt_KitsuHost_textChanged)

        hbox1.addWidget(lbl_Host)
        hbox1.addWidget(txt_KitsuHost)

        hbox2 = QtWidgets.QHBoxLayout()

        lbl_User = QtWidgets.QLabel('User: ', window)
        lbl_User.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_User.setFixedSize(108, 28)
        lbl_User.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_KitsuUser = QtWidgets.QLineEdit(self.kitsu_user, window)
        txt_KitsuUser.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_KitsuUser.setMinimumSize(280, 28)
        txt_KitsuUser.move(128,0)
        txt_KitsuUser.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454}')
        txt_KitsuUser.textChanged.connect(txt_KitsuUser_textChanged)

        hbox2.addWidget(lbl_User)
        hbox2.addWidget(txt_KitsuUser)

        hbox3 = QtWidgets.QHBoxLayout()

        lbl_Pass = QtWidgets.QLabel('Password: ', window)
        lbl_Pass.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_Pass.setFixedSize(108, 28)
        lbl_Pass.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_KitsuPass = QtWidgets.QLineEdit(self.kitsu_pass, window)
        txt_KitsuPass.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_KitsuPass.setMinimumSize(280, 28)
        txt_KitsuPass.move(128,0)
        txt_KitsuPass.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454}')
        txt_KitsuPass.setEchoMode(QtWidgets.QLineEdit.Password)
        txt_KitsuPass.textChanged.connect(txt_KitsuPass_textChanged)
        kitsu_pass_toggle_action = QtWidgets.QAction(window)
        kitsu_pass_toggle_action.setIcon(QtGui.QIcon('resources/eye.png'))
        kitsu_pass_toggle_action.triggered.connect(toggle_kitsu_password_visibility)
        txt_KitsuPass.addAction(kitsu_pass_toggle_action, QtWidgets.QLineEdit.TrailingPosition)

        hbox3.addWidget(lbl_Pass)
        hbox3.addWidget(txt_KitsuPass)

        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        vbox1.addLayout(hbox3)

        lbl_KitsuStatus = QtWidgets.QLabel(self.kitsu_status, window)
        lbl_KitsuStatus.setStyleSheet('QFrame {color: #989898; background-color: #373737; padding-left: 8px;}')
        lbl_KitsuStatus.setFixedHeight(28)
        lbl_KitsuStatus.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        kitsu_connect_btn = QtWidgets.QPushButton('Connect', window)
        kitsu_connect_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        kitsu_connect_btn.setMinimumSize(100, 28)
        kitsu_connect_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                'QPushButton:pressed {font:italic; color: #d9d9d9}')
        kitsu_connect_btn.clicked.connect(txt_KitsuConnect_Clicked)
        if self.kitsu_connector.gazu_client:
            kitsu_connect_btn.setText('Disconnect')
        self.kitsu_connect_btn = kitsu_connect_btn

        hbox4 = QtWidgets.QHBoxLayout()
        hbox4.addWidget(lbl_KitsuStatus)
        hbox4.addWidget(kitsu_connect_btn)
        vbox1.addLayout(hbox4)

        '''
        hbox_spacer = QtWidgets.QHBoxLayout()
        lbl_spacer = QtWidgets.QLabel('', window)
        lbl_spacer.setMinimumHeight(8)
        hbox_spacer.addWidget(lbl_spacer)
        vbox1.addLayout(hbox_spacer)
        '''

        # Flapi login box
        flapi_vbox1 = QtWidgets.QVBoxLayout()

        lbl_Flapi = QtWidgets.QLabel('Flapi Server: ', window)
        lbl_Flapi.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_Flapi.setFixedHeight(28)
        lbl_Flapi.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        flapi_vbox1.addWidget(lbl_Flapi)
    
        flapi_hbox1 = QtWidgets.QHBoxLayout()
        lbl_FlapiHost = QtWidgets.QLabel('Server: ', window)
        lbl_FlapiHost.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiHost.setFixedSize(108, 28)
        lbl_FlapiHost.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_FlapiHost = QtWidgets.QLineEdit(self.flapi_host, window)
        txt_FlapiHost.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_FlapiHost.setMinimumSize(280, 28)
        # txt_KitsuHost.move(128,0)
        txt_FlapiHost.setStyleSheet(
            'QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454;}'
            )
        txt_FlapiHost.textChanged.connect(txt_FlapiHost_textChanged)

        flapi_hbox1.addWidget(lbl_FlapiHost)
        flapi_hbox1.addWidget(txt_FlapiHost)
        flapi_vbox1.addLayout(flapi_hbox1)
        
        flapi_hbox2 = QtWidgets.QHBoxLayout()

        lbl_FlapiKey = QtWidgets.QLabel('API Key: ', window)
        lbl_FlapiKey.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiKey.setFixedSize(108, 28)
        lbl_FlapiKey.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_FlapiKey = QtWidgets.QLineEdit(self.kitsu_pass, window)
        txt_FlapiKey.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_FlapiKey.setMinimumSize(280, 28)
        txt_FlapiKey.move(128,0)
        txt_FlapiKey.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454}')
        txt_FlapiKey.setEchoMode(QtWidgets.QLineEdit.Password)
        txt_FlapiKey.textChanged.connect(txt_FlapiKey_textChanged)
        flapikey_toggle_action = QtWidgets.QAction(window)
        flapikey_toggle_action.setIcon(QtGui.QIcon('resources/eye.png'))
        flapikey_toggle_action.triggered.connect(toggle_flapikey_visibility)
        txt_FlapiKey.addAction(flapikey_toggle_action, QtWidgets.QLineEdit.TrailingPosition)


        flapi_hbox2.addWidget(lbl_FlapiKey)
        flapi_hbox2.addWidget(txt_FlapiKey)
        flapi_vbox1.addLayout(flapi_hbox2)

        flapi_hbox3 = QtWidgets.QHBoxLayout()

        lbl_FlapiStatus = QtWidgets.QLabel('Connected: ', window)
        lbl_FlapiStatus.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiStatus.setFixedHeight(28)
        lbl_FlapiStatus.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        flapi_connect_btn = QtWidgets.QPushButton('Connect', window)
        flapi_connect_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        flapi_connect_btn.setMinimumSize(100, 28)
        flapi_connect_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                'QPushButton:pressed {font:italic; color: #d9d9d9}')
        flapi_connect_btn.clicked.connect(txt_FlapiConnect_Clicked)
        self.flapi_connect_btn = flapi_connect_btn
        # kitsu_connect_btn.setDefault(True)

        flapi_hbox3.addWidget(lbl_FlapiStatus)
        flapi_hbox3.addWidget(flapi_connect_btn)
        flapi_vbox1.addLayout(flapi_hbox3)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(vbox1)
        vbox.addLayout(flapi_vbox1)

        exit_btn = QtWidgets.QPushButton('Exit', window)
        exit_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        exit_btn.setMinimumSize(100, 28)
        exit_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                            'QPushButton:pressed {font:italic; color: #d9d9d9}')
        exit_btn.clicked.connect(self.close_application)

        vbox.addWidget(exit_btn)

        self.setLayout(vbox)

        return window

    def close_application(self):
        QtWidgets.QApplication.instance().quit()
        # self.quit()

