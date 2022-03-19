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
    sys.argv[1] = sys.argv[1].lower().replace(" ", "_")
    with hashbrowns.Hashbrown(password=sys.argv[1], build_mode=False) as hashbrown:

        data = hashbrown.decrypted_data

        # Increment build version
        version_string = datetime.now().strftime('%y%m%d')
        data["Version"] = int(version_string)

        hashbrown.encrypted_data = hashbrown.encrypt(data)
        hashbrown.write_encrypted()

    with hashbrowns.Hashbrown(password=sys.argv[1], build_mode=True) as hashbrown:

        my_date = datetime.now()
        string = 'Print Queue Program V.'+my_date.strftime('%y%m%d')

        PyInstaller.__main__.run([
            '--clean',
            '--name=%s' % string,
            '--onefile',
            '--windowed',
            '--add-data=resources/iForge_logo_no_background_small.png;resources/',
            '--add-data=print_submission.py;.',
            '--add-data=resources/secrets.json.enc;resources/',
            '--add-data=file_dialog.py;/',
            '--add-data=gcode_parse.py;.',
            '--add-data=gdrive_upload.py;.',
            '--add-data=resources/iForge_logo_no_background_small.png;resources/',
            '--add-data=resources/printq50.png;resources/',
            '--add-data=resources/printq50icon.ico;resources/',
            '--add-data=serviceaccount.json;.',
            '--add-data=progress_bar.py;.',
            '--icon=%s' % os.path.join('resources/printq50icon.ico'),
            os.path.join('main.py'),
        ])

        print("\n\nBuild complete\n")

        os.remove(string+".spec")

        shutil.rmtree("build")
        shutil.rmtree("__pycache__")

        print("Build files deleted\n")