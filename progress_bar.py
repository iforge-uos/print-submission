
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QProgressBar
import get_path


class The_Bar(QDialog):
    # Setup the UI and get the current status of the George Porter key on creation.
    def __init__(self):
        super(The_Bar, self).__init__()

    def setConfig(self, cfg):
        self.Config = cfg

    # Setup UI
    def initUi(self):
        self.setFixedSize(300, 120)
        self.setWindowIcon(QIcon(get_path.go('resources/printq50.png')))
        self.setWindowTitle('Upload in progress...')
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.Message = QLabel("Uploading " + self.Config["filename"])
        self.Message.setWordWrap(True)
        self.Message2 = QLabel("")

        vBox = QVBoxLayout()
        self.Message.setAlignment(QtCore.Qt.AlignCenter)
        vBox.addWidget(self.Message)
        vBox.addWidget(self.progress)
        vBox.addWidget(self.Message2)

        self.setLayout(vBox)
    def update(self,val):
        self.progress.setValue(int(val))
