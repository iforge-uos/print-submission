from PyQt5.QtWidgets import *
import gcode_parse
import os



class App(QWidget):
    def __init__(self): #UI boilerplate
        super().__init__()

    def setConfig(self, cfg):
        self.Config = cfg


    def get_download_path(self):
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'downloads')

    def openFileNameDialog_GCODE(self):#Actual gubbins
        location = self.get_download_path()
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        #QFileDialog.setSidebarUrls([QtCore.QUrl.fromLocalFile(downloads)])
        fileName, _ = QFileDialog.getOpenFileName(self,"IForge GCode uploader", location,"Printing files (*.gcode)", options=options) #opens a single file dialog box that only accepts gcode
        print(fileName)
        fileName,short = self.MinorChecks(fileName)
        return(fileName,short)

    def openFileNameDialog_STL(self):#Actual gubbins
        location = self.get_download_path()
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        #QFileDialog.setSidebarUrls([QtCore.QUrl.fromLocalFile(downloads)])
        fileName, _ = QFileDialog.getOpenFileName(self,"IForge STL uploader", location,"Mesh files (*.STL)", options=options) #opens a single file dialog box that only accepts gcode
        
        short = os.path.basename(fileName)
        return fileName,short
        # status,id = gdrive_upload.run(fileName,short,self)
        # if status ==1:
        #     print("upload done")

    def MinorChecks(self, fileName):
        short = os.path.basename(fileName)
        error = False
        if fileName != "":
            size = os.path.getsize(fileName)
            if size >= 20000000:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)

                msg.setText("This is a big file, it may take a bit of time to process.")
                msg.setWindowTitle("Just a heads up")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
            details, error = gcode_parse.run(fileName,short)
            self.Config["length"] = details["filament_used"]["mm"]
            print("File selected")

        if fileName == "":
            # global weight
            length = 0
            print("no details")
            details = None

        self.Config["details"] = details

        try:
            return fileName, short
        except Exception:
            return