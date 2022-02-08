import sys
import PyInstaller.__main__
import os
import shutil
import re
import fileinput
from datetime import datetime
import json
import hashbrowns

if __name__ == "__main__":

    with hashbrowns.Hashbrown(password=sys.argv[1], build_mode=True) as hashbrown:

        data = hashbrown.decrypted_data

        # Increment build version
        version_string = datetime.now().strftime('%y%m%d')
        data["Version"] = int(version_string)

        my_date = datetime.now()
        string = 'Print Queue Program V.'+my_date.strftime('%y%m%d')

        PyInstaller.__main__.run([
            '--clean',
            '--name=%s' % string,
            '--onefile',
            '--windowed',
            '--add-data=resources/iForge_logo_no_background_small.png:resources/',
            '--add-data=print_submission.py:.',
            '--add-data=secrets.json:.',
            '--add-data=file_dialog.py:/',
            '--add-data=gcode_parse.py:.',
            '--add-data=gdrive_upload.py:.',
            '--add-data=resources/iForge_logo_no_background_small.png:resources/',
            '--add-data=printq50.png:resources/',
            '--add-data=printq50icon.ico:resources/',
            '--add-data=serviceaccount.json:.',
            '--add-data=progress_bar.py:.',
            '--icon=%s' % os.path.join('resources/printq50icon.ico'),
            os.path.join('main.py'),
        ])

        print("\n\nBuild complete\n")

        os.remove(string+".spec")

        shutil.rmtree("build")
        shutil.rmtree("__pycache__")

        print("Build files deleted\n")