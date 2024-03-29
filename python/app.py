import os
import sys
import base64
import getpass
import queue
import time
import threading
import inspect
import ctypes

from PyQt5 import QtGui, QtWidgets, QtCore

from .kitsu import appKitsuConnector
from .baselight import appBaselightConnector

from pprint import pprint, pformat

class FramelessWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(
                QtCore.Qt.Window | QtCore.Qt.Tool 
            )
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self._old_pos = None

    def mousePressEvent(self, event):
        self._old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self._old_pos = None

    def mouseMoveEvent(self, event):
        if self._old_pos:
            delta = event.pos() - self._old_pos
            self.move(self.pos() + delta)

    def closeEvent(self, event):
        event.accept()  # let the window close
        self.close_application()

    def close_application(self):
        QtWidgets.QApplication.instance().quit()
        # self.quit()

class TerminalWidget(QtWidgets.QPlainTextEdit):
    from PyQt5.QtCore import pyqtSignal, pyqtSlot
    # Define a new signal called 'append_signal' that takes a single str argument
    append_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(TerminalWidget, self).__init__(parent)
        self.setReadOnly(True)  # Make the text edit read only
        self.setMaximumBlockCount(255)  # Set the maximum number of lines
        self.setFixedHeight(120)
        self.setStyleSheet("""
            QPlainTextEdit {
                color: #888888;
                background-color: #373737;
                border: 1px solid #989898;
                border-radius: 4px;
                font-size: 12px;
            }

            QPlainTextEdit QScrollBar:vertical {
                border: none;
                background: #2A2929;
                width: 8px;
            }

            QScrollBar::handle:vertical {
                background: #605F5F;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            """)
        self.append_signal.connect(self.append_slot)

    @pyqtSlot(str)
    def append_slot(self, text):
        try:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if '\r' in line:
                    self.moveCursor(QtGui.QTextCursor.End)
                    self.moveCursor(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
                    self.textCursor().removeSelectedText()
                    self.appendPlainText(line.rstrip('\r'))
                else:
                    self.appendPlainText(line)

            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())  # Auto scroll to the bottom
        except:
            pass

    def append(self, text):
        # Emit the 'append_signal' with the text
        self.append_signal.emit(text)

class blMenuKITSU(FramelessWindow):
    # Define a custom signal
    allEventsProcessed = QtCore.pyqtSignal()
    showMessageBox = QtCore.pyqtSignal(str)
    setText = QtCore.pyqtSignal(dict)

    class MainLoop(QtCore.QThread):
        populateProjectList = QtCore.pyqtSignal()

        def run(self):
            parent = self.parent()
            prev_kitsu_data = dict(parent.framework.kitsu_data)

            while parent.threads:
                if pformat(prev_kitsu_data) != pformat(parent.framework.kitsu_data):
                    prev_kitsu_data = dict(parent.framework.kitsu_data)
                    self.populateProjectList.emit()
                    # pprint (parent.framework.kitsu_data.get('active_projects'))
                time.sleep(0.1)
            # Do some work...
            # for project_name in sorted(project_names):
            #    self.add_action_signal.emit(project_name)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.framework = kwargs.get('framework')
        self.prefs = self.framework.prefs
        self.name = self.__class__.__name__

        # set intermediate status
        self.kitsu_status = 'Ilde'
        self.bl_status = 'Idle'

        self.kitsu_connector = None
        self.bl_connector = None

        self.kitsu_current_project = {}
        self.kitsu_current_episode = {}

        self.defined_actions = [
            {'code': 1, 
                'name': 'Baselight Scene to Kitsu',
                'method': self.baselight_scene_to_kitsu},
            {'code': 2,
                'name': 'Update All Thumbnails',
                'method': self.render_update_thumbnails},
            {'code': 3,
                'name': 'Update Missing Thumbnails',
                'method': self.render_update_missing_thumbnails}
        ]
        self.current_action = {'code': 0, 'name': 'Select Action'}
        self.action_thread = None
        self.processing = False

        # A flag to check if all events have been processed
        self.allEventsFlag = False
        # Connect the signal to the slot
        self.allEventsProcessed.connect(self.on_allEventsProcessed)
        self.showMessageBox.connect(self.on_showMessageBox)
        self.setText.connect(self.on_setText)

        self.main_window()
        self.setStyleSheet("background-color: rgb(49, 49, 49);")
        self.show()

        self.loops = []
        self.threads = True
        self.loops.append(threading.Thread(target=self.process_messages))
        self.loops.append(threading.Thread(target=self.kitsu_loop, args=(8, )))

        # self.loops.append(threading.Thread(target=self.cache_short_loop, args=(8, )))
        # self.loops.append(threading.Thread(target=self.cache_long_loop, args=(8, )))
        # self.loops.append(threading.Thread(target=self.cache_utility_loop, args=(1, )))

        for loop in self.loops:
            loop.daemon = True
            loop.start()

        self.main_loop = self.MainLoop(self)
        self.main_loop.populateProjectList.connect(self.populate_project_list)
        self.main_loop.start()
        
        QtCore.QTimer.singleShot(0, self.after_show)
        self.populate_actions_list()

        # self.kitsu_connect_btn.click()
        # self.flapi_connect_btn.click()

    def processEvents(self):
        QtWidgets.QApplication.instance().processEvents()
        self.allEventsProcessed.emit()
        while not self.allEventsFlag:
            time.sleep(0.01)

    def on_allEventsProcessed(self):
        self.allEventsFlag = True

    def on_showMessageBox(self, message):
        mbox = QtWidgets.QMessageBox()
        mbox.setWindowFlags(QtCore.Qt.Tool)
        mbox.setStyleSheet("""
            QMessageBox {
                background-color: #313131;
                color: #9a9a9a;
                text-align: center;
            }
            QMessageBox QPushButton {
                width: 80px;
                height: 24px;
                color: #9a9a9a;
                background-color: #424142;
                border-top: 1px inset #555555;
                border-bottom: 1px inset black
            }
            QMessageBox QPushButton:pressed {
                font:italic;
                color: #d9d9d9
            }
        """)
        mbox.setText(message)
        mbox.exec_()

    def on_setText(self, item):
        widget_name = item.get('widget', 'unknown')
        text = item.get('text', 'unknown')
        if hasattr(self, widget_name):
            getattr(self, widget_name).setText(text)
            if widget_name.endswith('Status'):
                self.UI_setLabelColour(getattr(self, widget_name))
        self.processEvents()

    def connect_to_kitsu(self, msg = False):
        def connect_to_kitsu_thread(self, msg):
            try:
                self.framework.load_prefs()
                self.kitsu_host = self.prefs.get('kitsu_host', 'http://localhost/api/')
                self.kitsu_user = self.prefs.get('kitsu_user', 'user@host')
                self.kitsu_pass = ''
                encoded_kitsu_pass = self.prefs.get('kitsu_pass', '')
                if encoded_kitsu_pass:
                    self.kitsu_pass = base64.b64decode(encoded_kitsu_pass).decode("utf-8")

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_KitsuHost',
                    'text': self.kitsu_host}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_KitsuUser',
                    'text': self.kitsu_user}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_KitsuPass',
                    'text': self.kitsu_pass}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_lbl_KitsuStatus',
                    'text': 'Connecting...'}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_kitsu_connect_btn',
                    'text': 'Stop'}
                )

                self.kitsu_connector = appKitsuConnector(self.framework)
                if self.kitsu_connector:
                    self.kitsu_connector.get_user(msg)
                    self.kitsu_connector.init_pipeline_data()
                    self.kitsu_connector.scan_active_projects()

                if self.kitsu_connector.user:
                    self.kitsu_status = 'Connected'
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_lbl_KitsuStatus',
                        'text': 'Connected'}
                    )
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_kitsu_connect_btn',
                        'text': 'Disconnect'}
                    )
                else:
                    self.kitsu_status = 'Disconnected'
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_lbl_KitsuStatus',
                        'text': 'Disconnected'}
                    )
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_kitsu_connect_btn',
                        'text': 'Connect'}
                    )

            except Exception as e:
                self.framework.message_queue.put(
                        {'type': 'mbox',
                        'message': pformat(e)}
                )

        self.kitsu_status = 'Connecting'
        self.kitsu_connect_thread = threading.Thread(target=connect_to_kitsu_thread, args=(self, msg))
        self.kitsu_connect_thread.daemon = True
        self.kitsu_connect_thread.start()

        '''
        try:
            self.framework.load_prefs()
            self.kitsu_host = self.prefs.get('kitsu_host', 'http://localhost/api/')
            self.kitsu_user = self.prefs.get('kitsu_user', 'user@host')
            self.kitsu_pass = ''
            encoded_kitsu_pass = self.prefs.get('kitsu_pass', '')
            if encoded_kitsu_pass:
                self.kitsu_pass = base64.b64decode(encoded_kitsu_pass).decode("utf-8")
            self.flapi_host = self.prefs.get('flapi_host', 'localhost')
            self.flapi_user = self.prefs.get('flapi_user', getpass.getuser())
            self.flapi_pass = ''
            encoded_flapi_pass = self.prefs.get('flapi_pass', '')
            if encoded_flapi_pass:
                self.flapi_pass = base64.b64decode(encoded_flapi_pass).decode("utf-8")
            self.flapi_key = self.prefs.get('flapi_key', '')
            self.flapi_scenepath = self.prefs.get('bl_path', '')
            
            self.UI_txt_KitsuHost.setText(self.kitsu_host)
            self.UI_txt_KitsuUser.setText(self.kitsu_user)
            self.UI_txt_KitsuPass.setText(self.kitsu_pass)
            self.UI_txt_FlapiHost.setText(self.flapi_host)
            self.UI_txt_FlapiUser.setText(self.flapi_user)
            self.UI_txt_FlapiPass.setText(self.flapi_pass)
            self.UI_txt_FlapiKey.setText(self.flapi_key)
            self.UI_txt_FlapiScenePath.setText(self.flapi_scenepath)

            self.UI_lbl_KitsuStatus.setText('Connecting...')
            self.UI_setLabelColour(self.UI_lbl_KitsuStatus)
            self.processEvents()

            self.kitsu_connector = appKitsuConnector(self.framework)

            if self.kitsu_connector.user:
                self.kitsu_status = 'Connected'
                self.UI_lbl_KitsuStatus.setText('Connected')
                self.UI_setLabelColour(self.UI_lbl_KitsuStatus)
                self.UI_kitsu_connect_btn.setText('Disconnect')
            else:
                self.kitsu_status = 'Disconnected'
                self.UI_lbl_KitsuStatus.setText('Disconnected')
                self.UI_setLabelColour(self.UI_lbl_KitsuStatus)
                self.UI_kitsu_connect_btn.setText('Connect')

            self.processEvents()
        except Exception as e:
            self.showMessageBox.emit(pformat(e))
        '''

    def connect_to_flapi(self, msg = False):
        def connect_to_flapi_thread(self, msg):
            try:
                self.framework.load_prefs()
                self.flapi_host = self.prefs.get('flapi_host', 'localhost')
                self.flapi_user = self.prefs.get('flapi_user', getpass.getuser())
                self.flapi_pass = ''
                encoded_flapi_pass = self.prefs.get('flapi_pass', '')
                if encoded_flapi_pass:
                    self.flapi_pass = base64.b64decode(encoded_flapi_pass).decode("utf-8")
                self.flapi_key = self.prefs.get('flapi_key', '')
                self.flapi_scenepath = self.prefs.get('bl_path', '')

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_FlapiHost',
                    'text': self.flapi_host}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_FlapiUser',
                    'text': self.flapi_user}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_FlapiPass',
                    'text': self.flapi_pass}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_FlapiKey',
                    'text': self.flapi_key}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_txt_FlapiScenePath',
                    'text': self.flapi_scenepath}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_lbl_FlapiStatus',
                    'text': 'Connecting...'}
                )

                self.framework.message_queue.put(
                    {'type': 'setText',
                    'widget': 'UI_flapi_connect_btn',
                    'text': 'Stop'}
                )

                try:
                    self.bl_connector.fl_disconnect()
                    self.bl_connector = None
                except:
                    pass
                self.bl_connector = appBaselightConnector(self.framework)
                self.bl_connector.fl_connect(msg = msg)

                if self.bl_connector.conn:
                    self.bl_status = 'Connected'
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_lbl_FlapiStatus',
                        'text': 'Connected'}
                    )
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_flapi_connect_btn',
                        'text': 'Disconnect'}
                    )
                else:
                    self.bl_status = 'Disconnected'
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_lbl_FlapiStatus',
                        'text': 'Disconnected'}
                    )
                    self.framework.message_queue.put(
                        {'type': 'setText',
                        'widget': 'UI_flapi_connect_btn',
                        'text': 'Connect'}
                    )

                # self.bl_connector.fl_create_kitsu_menu()
            except Exception as e:
                self.framework.message_queue.put(
                        {'type': 'mbox',
                        'message': pformat(e)}
                )

        self.bl_status = 'Connecting'
        self.bl_connect_thread = threading.Thread(target=connect_to_flapi_thread, args=(self, msg))
        self.bl_connect_thread.daemon = True
        self.bl_connect_thread.start()

    def after_show(self):
        self.setMinimumSize(self.size())
        self.setFixedHeight(self.size().height())
        self.connect_to_kitsu()
        self.connect_to_flapi()

    def main_window(self):

        #QtWidgets.QApplication.instance().setStyleSheet("QLabel { color :  #999999; }")

        QtWidgets.QApplication.instance().setStyleSheet('''
            QLabel { 
                color :  #999999; 
            }
            QMenu {
                color: rgb(154, 154, 154);
                background-color: rgb(44, 54, 68);
                border: none;
                font: 14px;
            }
            QMenu::item {
                padding: 6px 10px;
                background-color: rgb(44, 54, 68)
            }
            QMenu::item:selected {
                background-color: rgb(73, 86, 99);
            }
            QMenu::item:hover {
                color: rgb(0, 0, 0);
                background-color: rgb(73, 86, 99);
            }
        ''')

        # pyinstaller resources path setting
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        eye_icon_path = os.path.join(base_path, 'resources', 'eye.png')

        self.kitsu_host_text = ''
        self.kitsu_user_text = ''
        self.kitsu_pass_text = ''
        self.flapi_host_text = ''
        self.flapi_user_text = ''
        self.flapi_pass_text = ''
        self.flapi_key_text = ''

        self.flapi_scenepath_text = ''


        def setLabelColour(label):
            if label.text() == 'Connected':
                label.setStyleSheet('QFrame {color: #449800; background-color: #373737; padding-left: 8px;}')
            elif label.text() == 'Connecting...':
                label.setStyleSheet('QFrame {color: #889800; background-color: #373737; padding-left: 8px;}')
            elif label.text() == 'Disconnected':
                label.setStyleSheet('QFrame {color: #994400; background-color: #373737; padding-left: 8px;}')
            else:
                label.setStyleSheet('QFrame {color: #989898; background-color: #373737; padding-left: 8px;}')
        self.UI_setLabelColour = setLabelColour

        def txt_KitsuHost_textChanged():
            self.kitsu_host_text = txt_KitsuHost.text()
            # storage_root_paths.setText(calculate_project_path())

        def txt_KitsuUser_textChanged():
            self.kitsu_user_text = txt_KitsuUser.text()

        def txt_KitsuPass_textChanged():
            self.kitsu_pass_text = txt_KitsuPass.text()

        def txt_KitsuConnect_Clicked():
            if self.kitsu_status == 'Connecting':
                self.terminate_thread(self.kitsu_connect_thread)
                self.kitsu_status = 'Disconnected'
                lbl_KitsuStatus.setText(self.kitsu_status)
                kitsu_connect_btn.setText('Connect')
            elif self.kitsu_status == 'Disconnected' or self.kitsu_status == 'Idle':
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
                if self.kitsu_connector:
                    self.kitsu_connector.gazu_client = None
                    self.kitsu_connector.user = None
                    self.kitsu_connector.user_name = None
                self.kitsu_status = 'Disconnected'
                lbl_KitsuStatus.setText(self.kitsu_status)
                kitsu_connect_btn.setText('Connect')
            setLabelColour(lbl_KitsuStatus)

        def txt_FlapiHost_textChanged():
            self.flapi_host_text = txt_FlapiHost.text()

        def txt_FlapiUser_textChanged():
            self.flapi_user_text = txt_FlapiUser.text()

        def txt_FlapiKey_textChanged():
            self.flapi_key_text = txt_FlapiKey.text()

        def txt_FlapiPass_textChanged():
            self.flapi_pass_text = txt_FlapiPass.text()

        def txt_FlapiScenePath_textChanged():
            self.flapi_scenepath_text = txt_FlapiScenePath.text()
            self.prefs['bl_path'] = self.flapi_scenepath_text

        def txt_FlapiConnect_Clicked():
            if self.bl_status == 'Connecting':
                self.terminate_thread(self.bl_connect_thread)
                self.bl_status = 'Disconnected'
                lbl_FlapiStatus.setText(self.bl_status)
                flapi_connect_btn.setText('Connect')
            elif self.bl_status == 'Disconnected' or self.bl_status == 'Idle':
                flapi_connect_btn.setText('Connecting...')
                self.flapi_host_text  = txt_FlapiHost.text()
                self.prefs['flapi_host'] = self.flapi_host_text
                self.prefs['flapi_user'] = self.flapi_user_text
                self.prefs['flapi_pass'] = base64.b64encode(self.flapi_pass_text.encode("utf-8")).decode("utf-8")
                self.prefs['flapi_key'] = self.flapi_key_text
                self.framework.save_prefs()
                self.bl_status = 'Connecting'
                self.connect_to_flapi(msg = True)
                if self.bl_connector:
                    if self.bl_connector.conn:
                        self.bl_status = 'Connected'
                        lbl_FlapiStatus.setText(self.bl_status)
                        flapi_connect_btn.setText('Disconnect')
                else:
                    self.bl_status = 'Disconnected'
                    flapi_connect_btn.setText('Connect')
                    lbl_FlapiStatus.setText(self.bl_status)
            else:
                self.bl_connector.fl_disconnect(msg = True)
                self.bl_status = 'Disconnected'
                lbl_FlapiStatus.setText(self.bl_status)
                flapi_connect_btn.setText('Connect')
            setLabelColour(lbl_FlapiStatus)

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

        def toggle_flapipass_visibility():
            if txt_FlapiPass.echoMode() == QtWidgets.QLineEdit.Password:
                txt_FlapiPass.setEchoMode(QtWidgets.QLineEdit.Normal)
            else:
                txt_FlapiPass.setEchoMode(QtWidgets.QLineEdit.Password)

        def set_selector_button_style(button):
            # button.setMinimumSize(QtCore.QSize(280, 28))
            button.setFixedHeight(28)
            # button.setMaximumSize(QtCore.QSize(150, 28))
            button.setFocusPolicy(QtCore.Qt.NoFocus)
            button.setStyleSheet(
            'QPushButton {color: rgb(154, 154, 154); background-color: rgb(44, 54, 68); border: none; font: 14px}'
            'QPushButton:hover {border: 1px solid rgb(90, 90, 90)}'
            'QPushButton:pressed {color: rgb(159, 159, 159); background-color: rgb(44, 54, 68); border: 1px solid rgb(90, 90, 90)}'
            'QPushButton:disabled {color: rgb(116, 116, 116); background-color: rgb(58, 58, 58); border: none}'
            'QPushButton::menu-indicator {image: none;}'
            )

        def btn_ActionProceed_Clicked():
            self.framework.save_prefs()
            if not self.processing:
                self.UI_action_proceed_btn.setText('Stop')
                self.processing = True
                self.action_thread = threading.Thread(target=self.process_action)
                self.action_thread.daemon = True
                self.action_thread.start()
            else:
                self.UI_action_proceed_btn.setText('Stopping...')
                self.processing = False
                self.bl_connector.processing_flag = False
                self.log('stopping...')
                if self.action_thread is not None:
                    self.action_thread.join()
                self.UI_action_proceed_btn.setText('Proceed')

        # window = QtWidgets.QWidget()
        window = self
        window.setWindowTitle(self.framework.app_name)
        window.setStyleSheet('background-color: #313131')
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.setMinimumSize(520, 840)
        # screen_res = QtWidgets.QDesktopWidget().screenGeometry()
        # window.move((screen_res.width()/2)-150, (screen_res.height() / 2) - 180)

        '''
        main_vbox = QtWidgets.QVBoxLayout(window)
        main_vbox.setSpacing(0)
        main_vbox.setContentsMargins(0, 0, 0, 0)

        # Create a new widget for the stripe at the top
        self.stripe_widget = QtWidgets.QWidget(window)
        self.stripe_widget.setStyleSheet("background-color: #474747;")
        self.stripe_widget.setFixedHeight(24)  # Adjust this value to change the height of the stripe

        # Create a label inside the stripe widget
        self.stripe_label = QtWidgets.QLabel("Your text here")  # Replace this with the text you want on the stripe
        self.stripe_label.setStyleSheet("color: #cbcbcb;")  # Change this to set the text color

        # Create a layout for the stripe widget and add the label to it
        stripe_layout = QtWidgets.QHBoxLayout()
        stripe_layout.addWidget(self.stripe_label)
        stripe_layout.addStretch(1)
        stripe_layout.setContentsMargins(18, 0, 0, 0)  # This will ensure the label fills the stripe widget

        # Set the layout to stripe_widget
        self.stripe_widget.setLayout(stripe_layout)

        # Add the stripe widget to the top of the main window's layout
        main_vbox.addWidget(self.stripe_widget)
        main_vbox.addSpacing(4)  # Add a 4-pixel space
        main_vbox.setContentsMargins(20, 20, 20, 20)
        '''

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

        txt_KitsuHost = QtWidgets.QLineEdit(self.kitsu_host_text, window)
        txt_KitsuHost.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_KitsuHost.setMinimumSize(280, 28)
        # txt_KitsuHost.move(128,0)
        txt_KitsuHost.setStyleSheet(
            'QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454;}'
            )
        txt_KitsuHost.textChanged.connect(txt_KitsuHost_textChanged)
        self.UI_txt_KitsuHost = txt_KitsuHost

        hbox1.addWidget(lbl_Host)
        hbox1.addWidget(txt_KitsuHost)

        hbox2 = QtWidgets.QHBoxLayout()

        lbl_User = QtWidgets.QLabel('User: ', window)
        lbl_User.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_User.setFixedSize(108, 28)
        lbl_User.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_KitsuUser = QtWidgets.QLineEdit(self.kitsu_user_text, window)
        txt_KitsuUser.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_KitsuUser.setMinimumSize(280, 28)
        txt_KitsuUser.move(128,0)
        txt_KitsuUser.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454}')
        txt_KitsuUser.textChanged.connect(txt_KitsuUser_textChanged)
        self.UI_txt_KitsuUser = txt_KitsuUser

        hbox2.addWidget(lbl_User)
        hbox2.addWidget(txt_KitsuUser)

        hbox3 = QtWidgets.QHBoxLayout()

        lbl_Pass = QtWidgets.QLabel('Password: ', window)
        lbl_Pass.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_Pass.setFixedSize(108, 28)
        lbl_Pass.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_KitsuPass = QtWidgets.QLineEdit(self.kitsu_pass_text, window)
        txt_KitsuPass.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_KitsuPass.setMinimumSize(280, 28)
        txt_KitsuPass.move(128,0)
        txt_KitsuPass.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454}')
        txt_KitsuPass.setEchoMode(QtWidgets.QLineEdit.Password)
        txt_KitsuPass.textChanged.connect(txt_KitsuPass_textChanged)
        kitsu_pass_toggle_action = QtWidgets.QAction(window)
        kitsu_pass_toggle_action.setIcon(QtGui.QIcon(eye_icon_path))
        kitsu_pass_toggle_action.triggered.connect(toggle_kitsu_password_visibility)
        txt_KitsuPass.addAction(kitsu_pass_toggle_action, QtWidgets.QLineEdit.TrailingPosition)
        self.UI_txt_KitsuPass = txt_KitsuPass

        hbox3.addWidget(lbl_Pass)
        hbox3.addWidget(txt_KitsuPass)

        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        vbox1.addLayout(hbox3)

        lbl_KitsuStatus = QtWidgets.QLabel(self.kitsu_status, window)
        setLabelColour(lbl_KitsuStatus)
        # lbl_KitsuStatus.setStyleSheet('QFrame {color: #989898; background-color: #373737; padding-left: 8px;}')
        lbl_KitsuStatus.setFixedHeight(28)
        lbl_KitsuStatus.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.UI_lbl_KitsuStatus = lbl_KitsuStatus

        kitsu_connect_btn = QtWidgets.QPushButton('Connect', window)
        kitsu_connect_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        kitsu_connect_btn.setMinimumSize(100, 28)
        kitsu_connect_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                'QPushButton:pressed {font:italic; color: #d9d9d9}')
        kitsu_connect_btn.clicked.connect(txt_KitsuConnect_Clicked)
        # if self.kitsu_status != 'Disconnected':
        #    kitsu_connect_btn.setText('Disconnect')
        self.UI_kitsu_connect_btn = kitsu_connect_btn

        hbox4 = QtWidgets.QHBoxLayout()
        hbox4.addWidget(lbl_KitsuStatus)
        hbox4.addWidget(kitsu_connect_btn)
        vbox1.addLayout(hbox4)

        hbox_scene_selector = QtWidgets.QHBoxLayout()

        # flow res selector button
        kitsu_project_selector = QtWidgets.QPushButton('Select Project')
        kitsu_project_selector.setContentsMargins(10, 0, 10, 0)
        set_selector_button_style(kitsu_project_selector)
        self.UI_kitsu_project_selector = kitsu_project_selector
        # hbox_scene_selector.addWidget(kitsu_project_selector, alignment=QtCore.Qt.AlignLeft)
        hbox_scene_selector.addWidget(kitsu_project_selector)
        hbox_scene_selector.addSpacing(4)
        hbox_scene_selector.setStretchFactor(kitsu_project_selector, 1)

        kitsu_episode_selector = QtWidgets.QPushButton('Select Episode')
        kitsu_episode_selector.setContentsMargins(10, 0, 10, 0)
        set_selector_button_style(kitsu_episode_selector)
        self.UI_kitsu_episode_selector = kitsu_episode_selector
        hbox_scene_selector.addWidget(kitsu_episode_selector)
        # hbox_scene_selector.addWidget(kitsu_episode_selector, alignment=QtCore.Qt.AlignRight)
        hbox_scene_selector.addSpacing(4)
        hbox_scene_selector.setStretchFactor(kitsu_episode_selector, 1)

        vbox1.addLayout(hbox_scene_selector)

        '''
        hbox_spacer = QtWidgets.QHBoxLayout()
        lbl_spacer = QtWidgets.QLabel('', window)
        lbl_spacer.setMinimumHeight(8)
        hbox_spacer.addWidget(lbl_spacer)
        vbox1.addLayout(hbox_spacer)
        '''

        # Flapi login box
        flapi_vbox1 = QtWidgets.QVBoxLayout()

        lbl_Flapi = QtWidgets.QLabel('Baselight Flapi Server Login: ', window)
        lbl_Flapi.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_Flapi.setFixedHeight(28)
        lbl_Flapi.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        flapi_vbox1.addWidget(lbl_Flapi)
    
        flapi_hbox1 = QtWidgets.QHBoxLayout()
        lbl_FlapiHost = QtWidgets.QLabel('Server: ', window)
        lbl_FlapiHost.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiHost.setFixedSize(108, 28)
        lbl_FlapiHost.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_FlapiHost = QtWidgets.QLineEdit(self.flapi_host_text, window)
        txt_FlapiHost.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_FlapiHost.setMinimumSize(280, 28)
        # txt_KitsuHost.move(128,0)
        txt_FlapiHost.setStyleSheet(
            'QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454;}'
            )
        txt_FlapiHost.textChanged.connect(txt_FlapiHost_textChanged)
        txt_FlapiHost.textChanged.connect(txt_FlapiHost_textChanged)
        self.UI_txt_FlapiHost = txt_FlapiHost

        flapi_hbox1.addWidget(lbl_FlapiHost)
        flapi_hbox1.addWidget(txt_FlapiHost)
        flapi_vbox1.addLayout(flapi_hbox1)

        flapi_hbox2 = QtWidgets.QHBoxLayout()
        lbl_FlapiUser = QtWidgets.QLabel('User: ', window)
        lbl_FlapiUser.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiUser.setFixedSize(108, 28)
        lbl_FlapiUser.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_FlapiUser = QtWidgets.QLineEdit(self.flapi_user_text, window)
        txt_FlapiUser.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_FlapiUser.setMinimumSize(280, 28)
        # txt_KitsuHost.move(128,0)
        txt_FlapiUser.setStyleSheet(
            'QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454;}'
            )
        txt_FlapiUser.textChanged.connect(txt_FlapiUser_textChanged)
        self.UI_txt_FlapiUser = txt_FlapiUser

        flapi_hbox2.addWidget(lbl_FlapiUser)
        flapi_hbox2.addWidget(txt_FlapiUser)
        flapi_vbox1.addLayout(flapi_hbox2)

        # ssh password field
        flapi_hbox_sshpass = QtWidgets.QHBoxLayout()
        lbl_FlapiPass = QtWidgets.QLabel('Password: ', window)
        lbl_FlapiPass.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiPass.setFixedSize(108, 28)
        lbl_FlapiPass.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        txt_FlapiPass = QtWidgets.QLineEdit(self.flapi_key_text, window)
        txt_FlapiPass.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_FlapiPass.setMinimumSize(280, 28)
        txt_FlapiPass.move(128,0)
        txt_FlapiPass.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454}')
        txt_FlapiPass.setEchoMode(QtWidgets.QLineEdit.Password)
        txt_FlapiPass.textChanged.connect(txt_FlapiPass_textChanged)
        flapipass_toggle_action = QtWidgets.QAction(window)
        flapipass_toggle_action.setIcon(QtGui.QIcon(eye_icon_path))
        flapipass_toggle_action.triggered.connect(toggle_flapipass_visibility)
        txt_FlapiPass.addAction(flapipass_toggle_action, QtWidgets.QLineEdit.TrailingPosition)
        self.UI_txt_FlapiPass = txt_FlapiPass
        flapi_hbox_sshpass.addWidget(lbl_FlapiPass)
        flapi_hbox_sshpass.addWidget(txt_FlapiPass)
        flapi_vbox1.addLayout(flapi_hbox_sshpass)

        flapi_hbox3 = QtWidgets.QHBoxLayout()

        lbl_FlapiKey = QtWidgets.QLabel('API Key: ', window)
        lbl_FlapiKey.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiKey.setFixedSize(108, 28)
        lbl_FlapiKey.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        txt_FlapiKey = QtWidgets.QLineEdit(self.flapi_pass_text, window)
        txt_FlapiKey.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_FlapiKey.setMinimumSize(280, 28)
        txt_FlapiKey.move(128,0)
        txt_FlapiKey.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454}')
        txt_FlapiKey.setEchoMode(QtWidgets.QLineEdit.Password)
        txt_FlapiKey.textChanged.connect(txt_FlapiKey_textChanged)
        flapikey_toggle_action = QtWidgets.QAction(window)
        flapikey_toggle_action.setIcon(QtGui.QIcon(eye_icon_path))
        flapikey_toggle_action.triggered.connect(toggle_flapikey_visibility)
        txt_FlapiKey.addAction(flapikey_toggle_action, QtWidgets.QLineEdit.TrailingPosition)
        self.UI_txt_FlapiKey = txt_FlapiKey

        flapi_hbox3.addWidget(lbl_FlapiKey)
        flapi_hbox3.addWidget(txt_FlapiKey)
        flapi_vbox1.addLayout(flapi_hbox3)

        flapi_hbox3 = QtWidgets.QHBoxLayout()

        lbl_FlapiStatus = QtWidgets.QLabel(self.bl_status, window)
        setLabelColour(lbl_FlapiStatus)
        # lbl_FlapiStatus.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiStatus.setFixedHeight(28)
        lbl_FlapiStatus.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.UI_lbl_FlapiStatus = lbl_FlapiStatus

        flapi_connect_btn = QtWidgets.QPushButton('Connect', window)
        flapi_connect_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        flapi_connect_btn.setMinimumSize(100, 28)
        flapi_connect_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                'QPushButton:pressed {font:italic; color: #d9d9d9}')
        flapi_connect_btn.clicked.connect(txt_FlapiConnect_Clicked)
        if self.bl_status != 'Disconnected':
            flapi_connect_btn.setText('Disconnect')
        self.UI_flapi_connect_btn = flapi_connect_btn
        
        # kitsu_connect_btn.setDefault(True)

        flapi_hbox3.addWidget(lbl_FlapiStatus)
        flapi_hbox3.addWidget(flapi_connect_btn)
        flapi_vbox1.addLayout(flapi_hbox3)

        # Baselight scene path
        lbl_FlapiScenePath = QtWidgets.QLabel('Baselight Scene Path: ', window)
        lbl_FlapiScenePath.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_FlapiScenePath.setFixedHeight(28)
        lbl_FlapiScenePath.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        txt_FlapiScenePath = QtWidgets.QLineEdit(self.flapi_scenepath_text, window)
        txt_FlapiScenePath.setFocusPolicy(QtCore.Qt.StrongFocus)
        txt_FlapiScenePath.setMinimumSize(280, 28)
        txt_FlapiScenePath.setStyleSheet(
            'QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #000000; border-bottom: 1px inset #545454;}'
            )
        txt_FlapiScenePath.textChanged.connect(txt_FlapiScenePath_textChanged)
        self.UI_txt_FlapiScenePath = txt_FlapiScenePath

        flapi_vbox1.addWidget(lbl_FlapiScenePath)
        flapi_vbox1.addWidget(txt_FlapiScenePath)

        # action selector and proceed button
        hbox_action_selector = QtWidgets.QHBoxLayout()
        action_selector = QtWidgets.QPushButton('Select Action')
        action_selector.setContentsMargins(10, 0, 10, 0)
        set_selector_button_style(action_selector)
        self.UI_action_selector = action_selector
        # hbox_scene_selector.addWidget(kitsu_project_selector, alignment=QtCore.Qt.AlignLeft)
        hbox_action_selector.addWidget(action_selector)
        hbox_action_selector.addSpacing(4)
        hbox_action_selector.setStretchFactor(action_selector, 1)

        action_proceed_btn = QtWidgets.QPushButton('Proceed', window)
        action_proceed_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        action_proceed_btn.setMinimumSize(80, 28)
        action_proceed_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                'QPushButton:pressed {font:italic; color: #d9d9d9}')
        action_proceed_btn.clicked.connect(btn_ActionProceed_Clicked)
        action_proceed_btn.setContentsMargins(10, 0, 10, 0)
        self.UI_action_proceed_btn = action_proceed_btn
        hbox_action_selector.addWidget(action_proceed_btn)
        hbox_action_selector.setStretchFactor(action_proceed_btn, 1)

        flapi_vbox1.addLayout(hbox_action_selector)

        terminal = TerminalWidget()
        self.UI_terminal = terminal

        vbox = QtWidgets.QVBoxLayout(window)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(vbox1)
        vbox.addLayout(flapi_vbox1)
        vbox.addWidget(terminal)

        exit_btn = QtWidgets.QPushButton('Exit', window)
        exit_btn.setFocusPolicy(QtCore.Qt.StrongFocus)
        exit_btn.setMinimumSize(100, 28)
        exit_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                            'QPushButton:pressed {font:italic; color: #d9d9d9}')
        exit_btn.clicked.connect(self.close_application)

        vbox.addWidget(exit_btn)

        # main_vbox.addLayout(vbox)
        self.setLayout(vbox)

        return window

    def process_messages(self):
        loop_timeout = 0.001
        while self.threads:
            try:
                item = self.framework.message_queue.get_nowait()
            except queue.Empty:
                if not self.threads:
                    break
                time.sleep(loop_timeout)
                continue
            if item is None:
                time.sleep(loop_timeout)
                continue
            if not isinstance(item, dict):
                self.framework.message_queue.task_done()
                time.sleep(loop_timeout)
                continue
            
            item_type = item.get('type')
            if not item_type:
                self.message_queue.task_done()
                time.sleep(loop_timeout)
                continue
            elif item_type == 'console':
                message = item.get('message')
                self.UI_terminal.append(message)
            elif item_type == 'setText':
                self.setText.emit(item)
            elif item_type == 'mbox':
                self.showMessageBox.emit(item.get('message'))
            else:
                self.message_queue.task_done()
                time.sleep(loop_timeout)
                continue
            
            self.framework.message_queue.task_done()
            time.sleep(loop_timeout)
        return

    def populate_actions_list(self):
        actions_menu = QtWidgets.QMenu(self)
        actions = self.defined_actions
        for a in sorted(actions, key=lambda x: x['code']):
            action = actions_menu.addAction(a.get('name'))
            x = lambda chk=False, a=a: self.select_action(a)
            action.triggered.connect(x)
        self.UI_action_selector.setMenu(actions_menu)

    def select_action(self, action):
        self.current_action = action
        self.UI_action_selector.setText(action.get('name'))

    def populate_project_list(self):
        project_menu = QtWidgets.QMenu(self)
        projects = self.framework.kitsu_data.get('active_projects', list())
        for project in sorted(projects, key=lambda x: x['name']):
            action = project_menu.addAction(project.get('name'))
            x = lambda chk=False, project=project: self.select_kitsu_project(project)
            action.triggered.connect(x)
        self.UI_kitsu_project_selector.setMenu(project_menu)

    def select_kitsu_project(self, project):
        self.kitsu_current_project = dict(project)
        self.UI_kitsu_project_selector.setText(project.get('name'))
        self.populate_episodes_list()

    def populate_episodes_list(self):
        if not self.kitsu_current_project:
            return
        current_project_id = self.kitsu_current_project.get('id')
        if not current_project_id:
            return
        episodes_menu = QtWidgets.QMenu(self)
        episodes_by_project_id = self.framework.kitsu_data.get('episodes_by_project_id', dict())
        episodes = episodes_by_project_id.get(current_project_id, list())
        for episode in sorted(episodes, key=lambda x: x['name']):
            action = episodes_menu.addAction(episode.get('name'))
            x = lambda chk=False, episode=episode: self.select_kitsu_episode(episode)
            action.triggered.connect(x)
        self.UI_kitsu_episode_selector.setMenu(episodes_menu)

    def select_kitsu_episode(self, episode):
        self.kitsu_current_episode = dict(episode)
        pprint (episode)
        self.UI_kitsu_episode_selector.setText(episode.get('name'))

    def process_action(self):
        def finish_action():
            self.processing = False
            self.log(f'Done with "{action_name}"')
            self.UI_action_proceed_btn.setText('Proceed')

        action_name = self.current_action.get('name')
        action_code = self.current_action.get('code')
        action_method = self.current_action.get('method')

        if not action_code > 0:
            self.showMessageBox.emit("Please select action to perform")
            finish_action()
            return
        
        if (self.kitsu_status == 'Diconnected') or (self.bl_status == 'Disconnected'):
            self.showMessageBox.emit("Kitsu and Flapi both has to be connected")
            finish_action()
            return

        bl_path = self.prefs.get('bl_path')

        if action_method:
            action_method(bl_path)

        finish_action()

    def baselight_scene_to_kitsu(self, bl_path):
        if (not self.kitsu_current_project) or (not self.kitsu_current_episode):
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Please select Kitsu project and episode'}
            )
            return False
        
        baselight_scene_info = {}
        baselight_scene_info['blpath'] = bl_path
        baselight_scene_info['project_id'] = self.kitsu_current_project.get('id')

        scene_path = self.bl_connector.fl_get_scene_path(bl_path)
        if not scene_path:
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to find Baselight scene: {bl_path}'}
            )
            return False
        
        if not self.bl_connector.is_scene_writable(scene_path):
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to open Baselight scene for writing'}
            )
            return False
        
        baselight_scene_info['scene_path'] = scene_path

        shots = self.bl_connector.get_baselight_scene_shots(scene_path)
        if not shots:
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to find any shots in scene: {bl_path}'}
            )
            return False

        baselight_scene_info['baselight_shots'] = shots

        kitsu_uid_metadata_obj = self.bl_connector.check_or_add_kitsu_metadata_definition(scene_path)
        if isinstance(kitsu_uid_metadata_obj, str):
            if kitsu_uid_metadata_obj.startswith('Error '):
                self.framework.message_queue.put(
                        {'type': 'mbox',
                        'message': kitsu_uid_metadata_obj}
                )
                return False

        baselight_scene_info['kitsu_uid_metadata_obj'] = kitsu_uid_metadata_obj

        kitsu_sequence = self.kitsu_connector.get_kitsu_sequence(
            self.kitsu_current_project,
            self.kitsu_current_episode,
            bl_path
            )
        
        if not kitsu_sequence:
            kitsu_sequence = self.kitsu_connector.create_kitsu_sequence(
                        self.kitsu_current_project,
                        self.kitsu_current_episode,
                        bl_path
                        )

        if not kitsu_sequence:
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to find or create sequence in kitsu'}
            )
            return False

        try:
            self.kitsu_connector.create_metadata_fields(self.kitsu_current_project)
        except Exception as e:
            self.log(f'Error creating metadata descriptors in Kitsu: {e}')

        baselight_scene_info['kitsu_sequence'] = kitsu_sequence
        kitsu_shots = self.kitsu_connector.get_shots_for_sequence(kitsu_sequence)
        baselight_scene_info['kitsu_shots'] = kitsu_shots

        new_shots = self.kitsu_connector.update_and_get_new_shots(baselight_scene_info)
        
        if not new_shots:
            return False
        
        if not self.bl_connector.is_scene_writable(scene_path):
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to open Baselight scene for writing'}
            )
            return False

        newly_created_shots = []
        for index, baselight_shot in enumerate(new_shots):
            shot_name = self.kitsu_connector.create_kitsu_shot_name(baselight_shot)
            shot_data = self.kitsu_connector.build_kitsu_shot_data(baselight_shot)
            new_shot = self.kitsu_connector.create_new_shot(
                self.kitsu_current_project,
                kitsu_sequence,
                shot_name,
                shot_data
            )
            if new_shot:
                self.log(f'Shot {new_shot.get("name")} ({index + 1} of {len(new_shots)}) created')
                baselight_shot['kitsu_shot'] = new_shot
                newly_created_shots.append(baselight_shot)
        
        if not self.bl_connector.is_scene_writable(scene_path):
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to open Baselight scene for writing. "kitsu-uid" metadata field will not be filled in Baselight scene. That would make thumbnails update impossible.'}
            )
            return False

        if newly_created_shots:
            response = self.bl_connector.set_kitsu_metadata(scene_path, newly_created_shots)
            if isinstance(response, str):
                if response.startswith('Error '):
                    self.framework.message_queue.put(
                            {'type': 'mbox',
                            'message': response}
                    )
                    return False
                
        self.framework.message_queue.put(
                {'type': 'mbox',
                'message': f'Created {len(newly_created_shots)} shots in Kitsu'}
        )
        return True
  
    def render_update_thumbnails(self, bl_path):
        if (not self.kitsu_current_project) or (not self.kitsu_current_episode):
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Please select Kitsu project and episode'}
            )
            return False
        
        baselight_scene_info = {}
        baselight_scene_info['blpath'] = bl_path
        baselight_scene_info['project_id'] = self.kitsu_current_project.get('id')

        scene_path = self.bl_connector.fl_get_scene_path(bl_path)
        if not scene_path:
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to find Baselight scene: {bl_path}'}
            )
            return False
        
        kitsu_shots = self.kitsu_connector.get_shots_for_episode(
            self.kitsu_current_episode
        )

        uploaded_uids, failed_uids = self.bl_connector.get_and_upload_thumbnails_from_kitsu_id(
            scene_path, 
            kitsu_shots,
            self.kitsu_connector)
        
        self.framework.message_queue.put(
                {'type': 'mbox',
                'message': f'Updated {len(uploaded_uids)} thumbnails.\nFailed to update {len(failed_uids)} thumbnails in Kitsu'}
        )
        return True

    def render_update_missing_thumbnails(self, bl_path):
        if (not self.kitsu_current_project) or (not self.kitsu_current_episode):
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Please select Kitsu project and episode'}
            )
            return False
        
        baselight_scene_info = {}
        baselight_scene_info['blpath'] = bl_path
        baselight_scene_info['project_id'] = self.kitsu_current_project.get('id')

        scene_path = self.bl_connector.fl_get_scene_path(bl_path)
        if not scene_path:
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': f'Unable to find Baselight scene: {bl_path}'}
            )
            return False
        
        kitsu_shots = self.kitsu_connector.get_shots_for_episode(
            self.kitsu_current_episode
        )

        kitsu_shots = self.kitsu_connector.shots_without_previews(kitsu_shots)

        uploaded_uids, failed_uids = self.bl_connector.get_and_upload_thumbnails_from_kitsu_id(
            scene_path, 
            kitsu_shots,
            self.kitsu_connector)
        
        self.framework.message_queue.put(
                {'type': 'mbox',
                'message': f'Updated {len(uploaded_uids)} thumbnails.\nFailed to update {len(failed_uids)} thumbnails in Kitsu'}
        )
        return True

    def close_application(self):
        self.framework.save_prefs()
        self.terminate_loops()
        if self.bl_connector:
            self.bl_connector.fl_disconnect()
        QtWidgets.QApplication.instance().quit()
        # self.quit()

    def kitsu_loop(self, timeout):
        avg_delta = timeout / 2
        recent_deltas = [avg_delta]*9
        while self.threads:
            start = time.time()
            
            if not self.kitsu_connector:
                time.sleep(0.1)
                continue

            if not self.kitsu_connector.user:
                time.sleep(1)
                continue

            if not self.kitsu_connector.user_name:
                time.sleep(1)
                continue
            
            try:
                self.kitsu_connector.collect_pipeline_data()
            except:
                pass

            # projects_by_id = {x.get('id'):x for x in self.pipeline_data['active_projects']}
            
            # self.collect_pipeline_data(current_project=current_project, current_client=shortloop_gazu_client)

            # self.gazu.log_out(client = shortloop_gazu_client)

            # self.preformat_common_queries()

            delta = time.time() - start
            self.log_debug('cache_short_loop took %s sec' % str(delta))

            last_delta = recent_deltas[len(recent_deltas) - 1]
            recent_deltas.pop(0)
            
            if abs(delta - last_delta) > last_delta*3:
                delta = last_delta*3

            recent_deltas.append(delta)
            avg_delta = sum(recent_deltas)/float(len(recent_deltas))
            if avg_delta > timeout/2:
                self.loop_timeout(avg_delta*2, start)
            else:
                self.loop_timeout(timeout, start)

    def cache_loop(self, timeout):
        avg_delta = timeout / 2
        recent_deltas = [avg_delta]*9
        while self.threads:
            start = time.time()
            
            if (not self.kitsu_connector) or (not self.bl_connector):
                time.sleep(0.1)
                continue

            if (not self.kitsu_connector.user) or (not self.bl_connector.conn):
                time.sleep(1)
                continue

            # projects_by_id = {x.get('id'):x for x in self.pipeline_data['active_projects']}
            
            # self.collect_pipeline_data(current_project=current_project, current_client=shortloop_gazu_client)

            # self.gazu.log_out(client = shortloop_gazu_client)

            # self.preformat_common_queries()

            delta = time.time() - start
            self.log_debug('cache_short_loop took %s sec' % str(delta))

            last_delta = recent_deltas[len(recent_deltas) - 1]
            recent_deltas.pop(0)
            
            if abs(delta - last_delta) > last_delta*3:
                delta = last_delta*3

            recent_deltas.append(delta)
            avg_delta = sum(recent_deltas)/float(len(recent_deltas))
            if avg_delta > timeout/2:
                self.loop_timeout(avg_delta*2, start)
            else:
                self.loop_timeout(timeout, start)

    def log(self, message):
        self.framework.log('[' + self.name + '] ' + str(message))

    def log_debug(self, message):
        self.framework.log_debug('[' + self.name + '] ' + str(message))

    def terminate_loops(self):
        self.threads = False
        
        for loop in self.loops:
            loop.join()

        self.main_loop.wait()

    def terminate_thread(self, thread):
        if not thread.is_alive():
            return

        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)

        if res == 0:
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': 'Terminating - Invalid thread id'}
            )
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
            self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': 'Terminating - PyThreadState_SetAsyncExc failed'}
            )

    def loop_timeout(self, timeout, start):
        time_passed = int(time.time() - start)
        if timeout <= time_passed:
            return
        else:
            for n in range(int(timeout - time_passed) * 10):
                if not self.threads:
                    self.log_debug('leaving loop thread: %s' % inspect.currentframe().f_back.f_code.co_name)
                    break
                time.sleep(0.1)
