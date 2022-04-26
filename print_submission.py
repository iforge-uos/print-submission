from progress_bar import The_Bar
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore

import get_path
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import file_dialog
import gdrive_upload
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
import datetime
# import Config
import re
import webbrowser
import os
import string
import traceback
import time
import LDAP
import PyQt5.QtWidgets
import pandas as pd

QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


# class test(QLabel):
#     clicked = pyqtSignal(str)
#     drooped = pyqtSignal(str)
#
#     def __init__(self, parent):
#         super(test, self).__init__(parent)
#         self.setAcceptDrops(True)
#
#     def dragEnterEvent(self, e):
#         print(e)
#
#         if e.mimeData().hasText():
#             e.accept()
#         else:
#             e.ignore()
#
#     def dropEvent(self, e):
#         print(e.mimeData().text())
#         self.drooped.emit(e.mimeData().text())
#
#     def mousePressEvent(self, event):
#         self.state = "click"
#
#     def mouseReleaseEvent(self, event):
#         if self.state == "click":
#             QTimer.singleShot(QApplication.instance().doubleClickInterval(), self.performSingleClickAction)
#
#     def performSingleClickAction(self):
#         if self.state == "click":
#             self.clicked.emit("")
#             print("EMIT")


class Validator(QtGui.QValidator):
    def validate(self, string, pos):
        return QtGui.QValidator.Acceptable, string.upper(), pos
        #Used later to ensure new text entered is upper case and displayed as such


class Print_queue_app(QWidget):
    def __init__(self, parent=None):
        # Not sure how this bit works but it does
        super(Print_queue_app, self).__init__(parent)

    def setConfig(self, cfg):
        self.Config = cfg

    def update_rep_names(self, force_reauth=False):
        if force_reauth:
            self.reAuth()

        UserBase = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("User Database")
        users = pd.DataFrame(UserBase.get_all_records(head=1))
        reps = users[users["rep_auth"] == 1]

        # generate rep name list, fallback on long name if no short provided
        rep_list = []
        for long, short in zip(reps["Name"], reps["short_name"]):
            if not short:
                rep_list.append(long)
            else:
                rep_list.append(short)

        self.Config["Rep_names"] = rep_list

    def startEverything(self):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
                      "https://www.googleapis.com/auth/spreadsheets"]

        self.creds = ServiceAccountCredentials._from_parsed_json_keyfile(self.Config["jason"], self.scope)
        self.client = gspread.authorize(self.creds)

        self.filing = file_dialog.App()
        self.filing.setConfig(self.Config)

        # Set the window properties, size it will occupy, position on screen and
        # give it an icon

        self.biglogopath = get_path.go('resources/iForge_logo_no_background_small.png')
        self.littlelogopath = get_path.go('resources/printq50.png')

        self.version_check()

        self.setWindowTitle("The Print Queue")
        self.setWindowIcon(QIcon(self.littlelogopath))

        screen = self.Config["app"].primaryScreen()
        size = screen.size()

        self.left = 820
        self.top = 240
        # Swidth = int(size.width() / 5.19)  # Dynamic display scaling, who even uses 1440p
        # Sheight = int(size.height() / 1.48)
        self.width = 370
        self.height = 730
        self.setMaximumWidth(370)

        self.setFixedSize(370, 730)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Set up iForge imgae as a pixmap
        self.logo = QLabel(self)

        self.logo.setPixmap(QPixmap(self.biglogopath))
        self.logo.setToolTip("Build " + str(self.Config["Version"]))

        # I hate the way this looks -AJM
        # SETTING DARK MODE
        if self.Config["dev_options"]["DarkMode"] == 1:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(69, 69, 69))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(69, 69, 69))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(19, 19, 19))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.setPalette(palette)
            # Setting Colour Overrides!

            self.stylesheet = """
                QWidget{color: rgb(255,255,255);}
                QPushButton{background-color: #4e4e4e;}
            """
            # Setting Pallete for Program
            self.setStyleSheet(self.stylesheet)

        self.path_GCODE = ""
        self.short_GCODE = ""
        self.path_STL = ""
        self.short_STL = ""

        # Set up the labels for data entry boxes

        myfont = QFont()
        myfont.setBold(True)

        # Headings go on the left and never change
        # Labels go on the right and may change
        # Boxes go on the right and are designed to be changed

        blank_heading = QLabel('')
        self.welcome_heading = QLabel(
            "If the app to crashes consistently, send me an email at ajmitchell1@sheffield.ac.uk, thanks!")
        # self.welcome_heading = QLabel("Send crash reports and feedbackIf you manage to get the app to crash, send me an email at ajmitchell1@sheffield.ac.uk describing what you did, Thanks!")
        self.name_heading = QLabel('Login: ')
        self.score_heading = QLabel('Level: ')
        self.project_heading = QLabel('Project type: ')
        self.rep_heading = QLabel('Rep name: ')
        gcode_heading = QLabel("File to upload:")
        self.status_heading = QLabel("Status:")
        self.review_cbox = QCheckBox("Request Review")

        self.score_label = QLabel('')
        self.gcode_label = QLabel("No file selected")
        self.stl_label = QLabel("No file selected")
        self.status_label = QLabel(" ")
        self.warning_label = QLabel(
            " Abuse of level permissions will not be tolerated. \nPunishment will be proportional.")
        self.warning_label.setFont(myfont)
        instruction_string = "Previous users are already registered Help and info can be found on our"
        hyperlink_string = "<a href='http://stackoverflow.com'>website</a>"
        # self.instruction_label = QLabel("Previous users are already registered<br>Help and info can be found on our "+hyperlink_string)
        self.instruction_label = QLabel(
            "Previous users are already registered<br>If you need help, give me a ring or shoot me a message, can almost always respond")

        self.instruction_label.setOpenExternalLinks(True)

        # Format one of the labels to allow wordwrap and creat bold version of font
        self.status_label.setWordWrap(True)
        self.welcome_heading.setWordWrap(True)
        self.instruction_label.setWordWrap(True)
        self.welcome_heading.setFont(myfont)

        # Set up the fields that can be edited (name etc)
        self.login_box = QLineEdit()

        self.validator = Validator(self)
        self.login_box.setValidator(self.validator)
        self.project_box = QLineEdit()
        self.rep_box = QLineEdit()

        # Set the placeholder text for some of the line edit boxes
        self.rep_box.setPlaceholderText("They will check your gcode")
        self.project_box.setPlaceholderText("Eg: Personal, FYP, MEC115")
        self.login_box.setPlaceholderText("Eg: FE6IF")

        self.update_rep_names()

        # This function checks if text has been changed in a field and colours
        # the box if the text change matches a criteria. Also serves to auto
        # capitalise names of reps
        def reptextchanged(text):
            if len(self.rep_box.text()) > 0 and len(self.rep_box.text()) < 2:
                # cap = string.capwords(self.rep_box.text())
                nocap = self.rep_box.text()
                self.rep_box.setText(nocap)
                # self.update_rep_names()
            if (self.rep_box.text() not in self.Config["Rep_names"]) and len(self.rep_box.text()) > 0:
                self.rep_box.setStyleSheet("background-color: rgb(255, 0, 0,50);")
            elif (self.rep_box.text() in self.Config["Rep_names"]):
                self.rep_box.setStyleSheet("background-color: rgb(0, 255, 0,50);")
            else:
                self.rep_box.setStyleSheet("background-color: rgb(255, 255, 255,100);")

        # Connect the text changed event to the function above
        self.rep_box.textChanged.connect(reptextchanged)

        def nametextchanged(text):
            self.score_label.setText("Searching")
            self.timer = QTimer()
            self.timer.setInterval(600)
            if re.match("[a-zA-Z]+[0-9]+[a-zA-Z]+", self.login_box.text()):
                self.timer.timeout.connect(self.credit_check)
            elif ".AC.UK" in self.login_box.text():
                self.timer.timeout.connect(self.credit_check)
            else:
                self.score_label.setText("")
            self.timer.start()

        # Connect the text changed event to the function above
        self.login_box.textChanged.connect(nametextchanged)

        # This part is the suggestion for names, just a means of standardising
        if self.Config["config_options"]["RepFill"] == 1:
            completer2 = QCompleter(self.Config["Rep_names"], self.rep_box)
            completer2.setCaseSensitivity(0)
            self.rep_box.setCompleter(completer2)
        if self.Config["config_options"]["RecentFill"] == 1:
            global completer
            completer = QCompleter(self.Config["RecentName"], self.login_box)
            completer.setCaseSensitivity(0)
            self.login_box.setCompleter(completer)

            def fill():
                if self.login_box.text() in self.Config["RecentName"]:
                    ind = self.Config["RecentName"].index(self.login_box.text())
                    self.project_box.setText(self.Config["RecentProject"][ind])

            self.login_box.textEdited.connect(fill)
            self.login_box.textChanged.connect(fill)

        # This part is for development purposes so i dont have to enter my
        # details every time
        if self.Config["dev_options"]["autofill"] == 1:
            self.login_box.setText("mea17ajm")
            self.rep_box.setText("Alistair M")
            self.project_box.setText("SOFTWARE TEST")

        # Set up the buttons and their headings
        self.submit_button = QPushButton('Submit')
        self.chooseGCODE_button = QPushButton('Choose file')
        self.chooseSTL_button = QPushButton('Choose file')

        # self.SButton.clicked.connect(self.get_file(location))

        # location2.join(location)
        # print(location)

        # Drag and drop button, removed to make working easier

        # self.SButton = test(self)
        # self.pix = QPixmap('./Drag_and_drop.png')
        # self.SButton.setPixmap(self.pix)
        # self.SButton.setAlignment(Qt.AlignCenter)
        # self.SButton.clicked.connect(extract_and_send)
        # self.SButton.drooped.connect(extract_and_send)

        self.sheet_button = QPushButton("View Queue Sheet")
        self.drive_button = QPushButton("View Queue Folder")
        self.cancel_button = QPushButton('Cancel')
        self.register_button = QPushButton('Register')

        # Initially set button to disabled so it cant be submitted
        self.submit_button.setDisabled(True)
        self.chooseSTL_button.setDisabled(True)
        self.chooseGCODE_button.setDisabled(True)

        # Connect the buttons with their respective functions for submission etc
        self.sheet_button.clicked.connect(self.sheet)
        self.drive_button.clicked.connect(self.drive)
        self.submit_button.clicked.connect(self.field_check)
        self.register_button.clicked.connect(self.RegisterUser)

        self.chooseGCODE_button.clicked.connect(self.extract_and_send)
        self.chooseSTL_button.clicked.connect(self.STL_and_send)

        self.cancel_button.clicked.connect(self.close)

        # This bit im still unsure about, it aims to try and set the width of the
        # line edit boxes but i just made the numbers by trial and error, i feel
        # that there is a better way to do this.
        width = 80

        self.name_heading.setFixedWidth(width)
        self.score_heading.setFixedWidth(width)
        self.project_heading.setFixedWidth(width)
        self.rep_heading.setFixedWidth(width)
        self.chooseGCODE_button.setFixedWidth(width)
        self.chooseSTL_button.setFixedWidth(width)
        self.status_heading.setFixedWidth(width + 20)
        gcode_heading.setFixedWidth(width + 20)

        self.status_label.setFixedHeight(80)

        self.login_box.setStyleSheet('color: rgb(0, 0, 0);')
        self.project_box.setStyleSheet('color: rgb(0, 0, 0);')
        self.rep_box.setStyleSheet('color: rgb(0, 0, 0);')

        # This whole section is setting up the UI, it feels a bit tedious but
        # everything is sorted into horizontal rows and then worked with from there

        hboxdemo = QHBoxLayout()
        hboxdemo.addWidget(self.welcome_heading)
        # self.welcome_heading.setAlignment(QtCore.Qt.AlignCenter)

        hBoxBlank = QHBoxLayout()
        hBoxBlank.addWidget(blank_heading)

        hBoxBlank2 = QHBoxLayout()
        hBoxBlank2.addWidget(blank_heading)

        hBoxBlank3 = QHBoxLayout()
        hBoxBlank3.addWidget(blank_heading)

        groupBox = QGroupBox("For the user to fill out:")

        hBoxName = QHBoxLayout()
        hBoxName.addWidget(self.name_heading)
        hBoxName.addWidget(self.login_box)

        self.hBoxLevel = QHBoxLayout()
        self.hBoxLevel.addWidget(self.score_heading)
        self.hBoxLevel.addWidget(self.score_label, Qt.AlignLeft)
        self.hBoxLevel.addWidget(self.register_button)
        self.register_button.setDisabled(True)

        hBoxProject = QHBoxLayout()
        hBoxProject.addWidget(self.project_heading)
        hBoxProject.addWidget(self.project_box)

        vBoxg = QVBoxLayout()
        vBoxg.addLayout(hBoxName)
        vBoxg.addLayout(self.hBoxLevel)
        vBoxg.addLayout(hBoxProject)

        groupBox.setLayout(vBoxg)

        self.togglebox_0 = QHBoxLayout()
        self.groupBox0 = QGroupBox()
        self.groupBox0.setTitle("Instructions on use:")
        hBox_toggle0 = QHBoxLayout()
        hBox_toggle0.addWidget(self.instruction_label)
        self.warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox0.setLayout(hBox_toggle0)
        self.groupBox0.setStyleSheet('QGroupBox  {color: #ed2023; font:bold 12px}')

        self.togglebox_1 = QHBoxLayout()
        self.groupBox1 = QGroupBox()
        self.groupBox1.setTitle("For the Rep to fill out:")
        hBoxRep = QHBoxLayout()
        hBoxRep.addWidget(self.rep_heading)
        hBoxRep.addWidget(self.rep_box)
        self.groupBox1.setLayout(hBoxRep)
        self.groupBox1.setStyleSheet('QGroupBox  {color: #ed2023; font:bold 12px}')

        self.togglebox_2 = QHBoxLayout()
        self.groupBox2 = QGroupBox()
        self.groupBox2.setTitle("Browse and upload .GCODE:")
        hBox_gcode = QHBoxLayout()
        hBox_gcode.addWidget(self.chooseGCODE_button)
        hBox_gcode.addWidget(self.gcode_label)
        hBox_status = QHBoxLayout()
        hBox_status.addWidget(self.status_heading)
        hBox_status.addWidget(self.status_label)

        vBox_toggle2 = QVBoxLayout()
        vBox_toggle2.addLayout(hBox_gcode)
        vBox_toggle2.addLayout(hBox_status)
        self.groupBox2.setLayout(vBox_toggle2)
        self.groupBox2.setStyleSheet('QGroupBox  {color: #ed2023; font:bold 12px}')

        self.togglebox_3 = QHBoxLayout()
        self.groupBox3 = QGroupBox()
        self.groupBox3.setTitle("Browse and upload .STL/3MF:")
        hBox_stl = QHBoxLayout()
        hBox_stl.addWidget(self.chooseSTL_button)
        hBox_stl.addWidget(self.stl_label)
        self.groupBox3.setLayout(hBox_stl)
        self.groupBox3.setStyleSheet('QGroupBox  {color: #ed2023; font:bold 12px}')

        self.togglebox_4 = QHBoxLayout()
        self.groupBox4 = QGroupBox()
        self.groupBox4.setTitle("Warning")
        hBox_toggle4 = QHBoxLayout()
        hBox_toggle4.addWidget(self.warning_label)
        self.warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox4.setLayout(hBox_toggle4)
        self.groupBox4.setStyleSheet('QGroupBox  {color: #ed2023; font:bold 12px}')

        groupBox.setStyleSheet('QGroupBox  {color: #ed2023; font:bold 12px}')

        # hBox_gcode.addWidget(self.SButton)

        hBoxReview = QHBoxLayout()
        hBoxReview.addWidget(self.review_cbox)

        hBoxSubmit = QHBoxLayout()
        hBoxSubmit.addWidget(self.submit_button)
        hBoxSubmit.addWidget(self.cancel_button)

        hBoxBrowse = QHBoxLayout()
        hBoxBrowse.addWidget(self.sheet_button)
        hBoxBrowse.addWidget(self.drive_button)

        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.logo)
        self.vBox.addLayout(hBoxBlank3)
        self.vBox.addLayout(hboxdemo)
        self.vBox.addLayout(hBoxBlank)

        self.vBox.addLayout(hBoxName)
        self.vBox.addWidget(groupBox, Qt.AlignTop)
        self.vBox.addLayout(self.togglebox_0, Qt.AlignTop)
        self.vBox.addLayout(self.togglebox_1, Qt.AlignTop)
        self.vBox.addLayout(self.togglebox_3, Qt.AlignTop)
        self.vBox.addLayout(self.togglebox_2, Qt.AlignTop)
        self.vBox.addLayout(hBoxBlank2, Qt.AlignTop)
        self.vBox.addLayout(hBoxReview)
        self.vBox.addLayout(hBoxSubmit)
        self.setLayout(self.vBox)
        if self.Config["config_options"]["View_buttons"] == 1:
            self.vBox.addLayout(hBoxBrowse)

        self.togglebox_0.addWidget(self.groupBox0)
        self.togglebox_2.addWidget(self.groupBox2)

    def credit_check(self):
        self.reAuth()
        print("Credit check in progress... contacting local banks")
        try:
            if self.login_box.text() == "":
                print("BLANK NAME")
                raise
            UserBase = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("User Database")

            login,name,email,score,level = UserBase.row_values(UserBase.find(self.login_box.text()).row)[0:5]

            # cell = UserBase.find(self.login_box.text()) #Struggle

            # name_cell = "B" + str(cell.row)
            # email_cell = "C" + str(cell.row)
            # score_cell = "D" + str(cell.row)
            # level_cell = "E" + str(cell.row)
            #
            # login = str(self.login_box.text())
            # name = str(UserBase.acell(name_cell).value) #Struggle
            # email = str(UserBase.acell(email_cell).value) #Struggle
            # score = str(UserBase.acell(score_cell).value) #Struggle
            # level = str(UserBase.acell(level_cell).value) #Struggle


            creditscore = level + " (" + score + ")"

            self.UserInfo = [login, name, email, level, score, creditscore]

            print("login IS: " + login)
            print("NAME IS: " + name)
            print("EMAIL IS: " + email)
            print("LEVEL IS: " + creditscore)
            self.score_label.setText(creditscore)
            self.SelectiveUI()
        except Exception as e:
            if self.login_box.text() == "":
                print("BLANK NAME EXCEPTION")
                creditscore = ""
                level = ""
            else:
                print("Not registered")
                creditscore = "Not registered"
                level = "None"
            self.score_label.setText(creditscore)

            self.UserInfo = [0, 0, 0, level, 0, creditscore]
            self.SelectiveUI()
        self.timer.stop()

    def extract_and_send(self, file):
        location = ""
        if file:
            location = format(file)
            location = location.replace('file:///', '')
        self.get_file(location)

    def STL_and_send(self):
        print("STL AND SEND")
        self.path_STL, self.short_STL = self.filing.openFileNameDialog_STL()
        print(self.path_STL)
        if self.path_STL:
            self.stl_label.setText(self.short_STL)
            self.file_check()

    # get_file is the function called to open a dialog box and return useful
    # stats from the gcode, it triggers a gcode parse within itself
    def get_file(self, location):
        global details
        global weight
        try:
            if location == "":
                print("Clicked")
                # self.filing.openFileNameDialog_GCODE()
                self.path_GCODE, self.short_GCODE = self.filing.openFileNameDialog_GCODE()
                # print("b= "+b)
            else:
                print("Dropped")
                self.filing.MinorChecks(location)
        except Exception:
            # Closing the dialog box during running triggers an exception,
            # i dont think this is a good way to do it
            print("oh no")
            raise  # return

        # This is the data handling from the gcode parse, displaying it in the
        # program so the rep can verify they have the correct file

        print(self.Config["details"])
        print(self.Config["length"])
        details = self.Config["details"]
        printer_oops = "non_iforge"
        if details == None:
            print("no file")
        else:
            print("item got")
            name = self.login_box.text()
            self.status_label.setStyleSheet('color:default')
            self.submit_button.setText("Submit")
            self.status_label.setText(" ")
            self.short_GCODE = details["filename"]
            self.path_GCODE = details["path"]
            time = re.findall('\d+', details["time_taken"])
            global hours
            hours = int(time[0])
            print(self.path_GCODE)
            if hours >= 10:
                self.status_label.setStyleSheet('color:red')
                self.submit_button.setText("Bit long isnt it?")
            if details["printer_type"] == printer_oops:
                self.gcode_label.setText(self.short_GCODE)
                self.status_label.setStyleSheet('color:red')
                self.status_label.setText("Unsupported printer or profile. \nMaybe get a rep to check the gcode again.")
                self.submit_button.setDisabled(True)
            elif details["printer_type"] == "Prusa MK2":
                self.gcode_label.setText(self.short_GCODE)
                self.status_label.setStyleSheet('color:red')
                self.status_label.setText("Prusa control may not be set up correctly.\n\nPlease reslice!")
                self.submit_button.setDisabled(True)
            elif details["printer_type"] == "non_iforge":
                self.gcode_label.setText(self.short_GCODE)
                self.status_label.setStyleSheet('color:red')
                self.status_label.setText("Sliced using non-iForge settings, please reslice using our presets")
                self.submit_button.setDisabled(True)
            else:
                self.gcode_label.setText(self.short_GCODE)
                self.status_label.setText(
                    f'Printer: {details["printer_type"]}\n'
                    f'Estimated time: {details["time_taken"]}\n'
                    f'Filament used: {details["filament_used"]["g"]:.3f}g\n'
                    f'Length: {details["filament_used"]["mm"] / 1000:.3f}m')
                # self.submit_button.setDisabled(False)
                weight = f"{details['filament_used']['g']}g"
                self.file_check()
        # This bit is to change the style to indicate our 10 hour soft limit



    def SelectiveUI(self):
        self.clearUI()

        level = self.UserInfo[3]
        print("select UI sees: " + level)

        if level == "":
            self.togglebox_0.addWidget(self.groupBox0)  # Instruction box
            self.register_button.setDisabled(True)
        elif level == "None":
            self.register_button.setDisabled(False)

        elif level == "Beginner":
            self.togglebox_1.addWidget(self.groupBox1)  # Rep login box
            self.togglebox_2.addWidget(self.groupBox2)  # GCODE submission box
            self.chooseGCODE_button.setDisabled(False)
        elif level == "Intermediate":
            print("MID TIER")
            self.togglebox_2.addWidget(self.groupBox2)  # GCODE submission box
            self.togglebox_3.addWidget(self.groupBox3)  # STL submission box
            self.chooseGCODE_button.setDisabled(False)
            self.chooseSTL_button.setDisabled(False)
        else:
            self.togglebox_2.addWidget(self.groupBox2)  # GCODE submission box
            self.togglebox_3.addWidget(self.groupBox4)  # warning box
            self.chooseGCODE_button.setDisabled(False)

            # self.togglebox_1.removeWidget(self.groupBox1)
        self.Config["app"].processEvents()

    def clearUI(self):
        self.register_button.setDisabled(True)
        self.chooseGCODE_button.setDisabled(True)
        self.chooseSTL_button.setDisabled(True)
        self.submit_button.setDisabled(True)
        self.groupBox0.setParent(None)
        self.groupBox1.setParent(None)
        # self.groupBox2.setParent(None)
        self.groupBox3.setParent(None)
        self.groupBox4.setParent(None)

    def next_available_row(self, worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list) + 1)

    def toggle(self):
        print(self.sizeHint())

    def RegisterUser(self):
        LDAP_Results = LDAP.go(self.login_box.text())
        if LDAP_Results[2] == "network error":
            print("Oops it looks like there was a " + LDAP_Results[2])
            self.error_handling(1)
        elif LDAP_Results[2] == "error in the submitted information":
            self.error_handling(5)
        else:
            print("LOGIN: " + self.login_box.text())
            print("EMAIL: " + LDAP_Results[1])
            if self.password() == "TRUE":
                UserBase = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("User Database")
                cell = self.next_available_row(UserBase)
                LevelText = ("=if(D" + cell + '="","", VLOOKUP(D' + cell + ',Score_Parameters!$A$2:$C$7,3))')
                UserBase.update_cell(cell, '1', self.login_box.text())  # Login
                UserBase.update_cell(cell, '2', string.capwords(LDAP_Results[0]))  # Name
                UserBase.update_cell(cell, '3', LDAP_Results[1])  # Email
                UserBase.update_cell(cell, '4', 0)  # Level
                UserBase.update_cell(cell, '5', LevelText)  # Level

                print("ADDED")
            self.credit_check()

    # This is a rudimentary version checking setup, within the spreadsheet there
    # is a cell dedicated to housing a version number, if the app is an old
    # version it will display a popup box

    def version_check(self):
        version = self.Config["Version"]
        global sheet
        try:
            sheet = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("Print Log")
            latest = int(sheet.acell("S2").value)
            if latest > version:
                print("oh dear ")
                self.error_handling(2)
                sys.exit(1)
        except Exception as e:
            raise e
            self.error_handling(6)
            sys.exit(1)

    # There was a rep who made me realise that this code may need some form of
    # competency check and/or warnings (Tylerproof).
    def error_handling(self, n):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(self.littlelogopath))
        if n == 2 or 6:
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)

        text = ["Please fill in all boxes",
                "It looks like there was a network error.\nAre you on the university network?",
                "This version of the program is critically out of date! \n\n Please download the latest version.",
                "The rep needs to match their name to the autofill.",
                "I'm sorry Dave, I'm afraid I can't do that",
                "The personal identifier you entered doesn't appear to be valid",
                "Cannot connect to internet, please try again with a valid connection"]
        msg.setText(text[n])
        # This is of course a reference to the film se7en
        msg.setWindowTitle("WHATS IN THE BOX!")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    # This function lets the user know a process has failed and keeps all the
    # data handy so they can resubmit
    def failedmessage(self):
        msg = QMessageBox.question(self, 'RUH ROH',
                                   "Dont know what happened there but it looks like the upload failed, do you want to try again?",
                                   QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.Yes:
            return (1)
        else:
            return (0)

    # This is what caused the big bug all along, access token for google sheets
    # was expiring after 60 mins
    def reAuth(self):
        print("Checking token,", end = ' ')
        if self.creds.access_token_expired:
            self.client.login()
            print("Reauthed")

        else:
            print("token good")

    # This is a function to reset all user input boxes and labels
    def clearall(self):
        self.project_box.setText("")
        self.login_box.setText("")
        self.rep_box.setText("")
        self.rep_box.setStyleSheet('color:rgb(0,0,0)')
        self.gcode_label.setText("No file selected")
        self.stl_label.setText("No file selected")
        self.status_label.setText("")
        self.submit_button.setDisabled(True)
        self.status_label.setStyleSheet('color:default')
        self.submit_button.setText("Submit")
        self.review_cbox.setChecked(False)

        self.update_rep_names(True)

    # This is the competency check. We check for full name, we check an email has
    # a "." or number present, we check the rep name is a registered rep and we
    # check that all the boxes have data
    def field_check(self):
        print("checking fields")
        level = self.UserInfo[3]

        if self.login_box.text() == "":
            print("Please enter an identifier")
            self.error_handling(0)
        elif self.project_box.text() == "":
            print("no project")
            self.error_handling(0)
        elif level == "Beginner" and self.rep_box.text() not in self.Config["Rep_names"]:
            print("Fill the rep box")
            self.error_handling(3)
        else:
            print("all good")
            if (level == "Beginner" and self.password() == "TRUE"):
                self.submit_file()
            elif (level != "Beginner"):
                self.submit_file()
            else:
                print("This previously contained self.submit_file, not a good call - AJM 05/04/2022")

    def file_check(self):
        print("checking file")

        # if self.path_GCODE != "":
        #     print(self.UserInfo[3])
        #     if self.path_STL !="" and self.UserInfo[3] == "Intermediate":
        #         self.submit_button.setDisabled(False)
        #         print("File accepted")
        #     else:
        #         self.submit_button.setDisabled(False)
        #         print("File accepted")

        if self.UserInfo[3] == "Intermediate":
            print(self.UserInfo[3])
            if self.path_STL != "" and self.path_GCODE != "":
                self.submit_button.setDisabled(False)
                print("File accepted")
        else:
            self.submit_button.setDisabled(False)
            print("File accepted")

    # Password function to check that the person submitting is actually a rep
    def password(self):
        msg2 = ""
        while self.Config["dev_options"]["password_submit"] == 1:
            # msg = "Before we can add this to the queue, we \nneed to 'charge' you for "+str(weight)+ "g of filament.\n\nAsk a rep at the front desk to put this through the till.\nThis wont actually cost, its just for tracking usage! \n\nPassword: \n"+msg2
            msg = "Password: \nHint: It isnt the same as last year" + msg2
            text, ok = QInputDialog.getText(self, "Password", msg, QLineEdit.Password)
            if ok == False:
                return "FALSE"
                break
            if text == "maker5pace":
                # Ah yes lets store the password as plain text, solid idea....
                # msg = QMessageBox()
                # msg.setIcon(QMessageBox.Information)
                # msg.setText("Just give the program some time to do its thing. \nYoull know when its done")
                # msg.setWindowTitle("Just a heads up")
                # msg.setWindowIcon(QIcon(self.littlelogopath))
                # msg.setStandardButtons(QMessageBox.Ok)
                # retval = msg.exec_()

                return "TRUE"
            else:
                print("wrong pwd")
                msg2 = "Incorrect password"
        else:
            return "TRUE"

    # This is of course the function to submit the actual file, both to google
    # drive and upload its various details to the spreadsheet.
    def submit_file(self):
        self.reAuth()

        level = self.UserInfo[3]

        self.path_GCODE = details["path"]
        self.short_GCODE = details["filename"]

        details["name"] = (self.UserInfo[1])  # Name
        details["email"] = (self.UserInfo[2])  # Email

        details["project_type"] = string.capwords(self.project_box.text())

        # Not sure if this bit works, needs checking
        if self.login_box.text() not in self.Config["RecentName"]:
            self.Config["RecentName"].append(self.login_box.text())
            self.Config["RecentProject"].append(self.project_box.text())
            self.Config["RecentName"] = self.Config["RecentName"][-5:]
            self.Config["RecentProject"] = self.Config["RecentProject"][-5:]
            print(self.Config["RecentName"])
            print(self.Config["RecentProject"])
            completer = QCompleter(self.Config["RecentName"], self.login_box)
            self.login_box.setCompleter(completer)

        # STL upload code
        if level == "Intermediate":
            print("STL uploading")
            self.Config["short"] = self.short_STL
            status, id_STL = gdrive_upload.run(self.path_STL, self.short_STL, self, self.Config)
            if status == 1:
                print("STL uploaded")
            else:
                keep = self.failedmessage()
                if keep == 0:
                    self.clearall()
                sheet.delete_row(rows)
                return

        print("GCODE uploading")
        self.Config["short"] = self.short_GCODE
        status, id_GCODE = gdrive_upload.run(self.path_GCODE, self.short_GCODE, self, self.Config)

        details["filename"] = f'=HYPERLINK("https://drive.google.com/u/0/uc?export=download&id={id_GCODE}",' \
                              f'"{self.short_GCODE}")'

        if status == 1:
            print("GCODE uploaded")

            # Initial spreadsheet entry
            details[
                "path"] = ""  # clear the array at 10 so we dont get it in the spreadsheet, just using as a variable conveyor
            self.status_label.setVisible(True)

            if level == "Intermediate":
                sheet = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("Need Approval")
                finalstatus = "Awaiting approval"
                hyperlink_irepcheck = '=HYPERLINK("https://drive.google.com/file/d/' + id_STL + '/view","STL")'
                details["rep_check"] = hyperlink_irepcheck
            else:
                sheet = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("Queue")

                # Stops us doing a manual check
                if hours >= 10 or self.review_cbox.isChecked():
                    finalstatus = "Under review"
                else:
                    finalstatus = "Queued"

                if level == "Beginner":
                    # details["rep_check"]=string.capwords(self.rep_box.text()) #CAPS
                    details["rep_check"] = self.rep_box.text()
                else:
                    details["rep_check"] = "Unchecked"

                if not re.findall("https://drive.google.com/file/d/", details["rep_check"]):
                    leaderboard_sheet = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("Leaderboard")
                    lb = pd.DataFrame(leaderboard_sheet.get_all_records(head=2))[
                        ["Fail & Reject rate", "Names"]].set_index("Names")
                    try:
                        err_perc = float(lb.loc[details["rep_check"], "Fail & Reject rate"].strip("%")) / 100.0
                        # if rep has a lot of failed/rejected prints
                        if err_perc >= 0.20:
                            finalstatus = "Under review"
                    except KeyError as e:
                        print(e)
                        # rep not in leaderboard, ie first print
                        finalstatus = "Under review"


            rows = sheet.row_count
            str_rows = str(rows)
            row_items = []  # list(details.values())
            for x in details["order"]:
                if x == "filament_used":
                    row_items.append(details[x]["g"])
                else:
                    row_items.append(details[x])

            sheet.insert_row(row_items, rows, value_input_option='USER_ENTERED')
            # if getting funny results make sure theres a free row at the base
            print("main details added")

            cell_id = f"G{str_rows}"
            # format as date (hide time)
            sheet.format(cell_id, {"numberFormat": {"type": "DATE", "pattern": "dd/mm/yyyy"}})

            sheet.update_cell(rows, '15', id_GCODE)

            formula1 = f'=IFERROR(if(P{str_rows}<>"", (D{str_rows}+P{str_rows}),""),"")'
            formula2 = "=IFERROR(if(I" + str_rows + '="complete", (NOW()-G' + str_rows + '),""),"")'
            # formula3 = "=AVERAGE(R" + str(int(rows) - 20) + ":R" + str_rows + ")"
            formula4 = '=COUNTIFS(K$4:K,K' + str_rows + ',I$4:I,"Running")'
            sheet.update_cell(rows, '17', formula1)
            sheet.update_cell(rows, '18', formula2)
            sheet.update_cell(rows, '19', formula4)
            sheet.update_cell(rows, '9', finalstatus)

            log_sheet = self.client.open_by_url(self.Config["spreadsheet"]).worksheet("Print Log")
            eta = log_sheet.acell("S1").value.split('\n')[1]

            self.clearall()
            self.clearUI()

            fulltime = datetime.datetime.now()
            time = fulltime.strftime("%H:%M:%S")
            queue = str(sheet.acell("I2").value)
            queuemore = str(sheet.acell("N1").value)
            self.ProgressBar.close()
            self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
            self.activateWindow()
            self.raise_()
            self.show()
            self.UserInfo = ["","","","","",""]
            self.SelectiveUI()
            useful_string = "Uploaded " + self.short_GCODE + " at " + time + ", you are number " + queue + " in the queue."
            eta_string = "\n Our best time estimate is:\n" + eta
            self.status_label.setText(useful_string)

            useful_string = "Uploaded " + self.short_GCODE + " at " + time + ", you are number " + queue + " in the queue."
            eta_string = "\n Our best time estimate is:\n" + eta
            status_string = useful_string
            self.status_label.setText(status_string)

            self.path_GCODE = ""
            self.short_GCODE = ""
            self.path_STL = ""
            self.short_STL = ""

        else:
            keep = self.failedmessage()
            if keep == 0:
                self.clearall()
            sheet.delete_row(rows)  # TODO: fix references to `sheet` when not declared, needs refactoring _a lot_ to `self.sheet` (same for `rows`)
            return

    def sheet(self):
        webbrowser.open_new(self.Config["spreadsheet"])

    def drive(self):
        webbrowser.open_new(self.Config["Queuefolder"])
