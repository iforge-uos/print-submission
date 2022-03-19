from PyQt5.QtWidgets import QApplication
import sys
import os
import json

import get_path
import hashbrowns
from print_submission import Print_queue_app


def main(cfg):
    app = QApplication(sys.argv)
    Config["app"] = app

    # Style setup, not a fan of this but can be subject to change

    # available = QStyleFactory.keys()
    # if 'Fusion' in available:
    #     print("FUSION")
    #     app.setStyle('Fusion')
    # elif 'Plastique' in available:
    #     print("PLAST")
    #     app.setStyle('Plastique')

    # Commented cos i dislike Fusion
    # global appWindow
    appWindow = Print_queue_app()
    appWindow.setConfig(cfg)
    appWindow.startEverything()
    appWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    # t = Thread(target=main)
    # t.start()
    # with open(get_path.go("secrets.json")) as file:
    #     Config = json.load(file)

    if len(sys.argv) > 1:
        py_cwd = sys.argv[1]
    else:
        cwd = os.getcwd()

    py_cwd = cwd.lower().replace(" ", "_")

    with hashbrowns.Hashbrown(py_cwd) as hashbrown:
        Config = hashbrown.decrypted_data

        try:
            main(Config)

        finally:
            print("eggo")
            # sys.exit(1)
