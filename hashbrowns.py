import get_path
import json

import base64
import os

import cryptography.fernet
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout

class PasswordPopup(QDialog):
    def __init__(self, msg, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Password")
        self.setLayout(QVBoxLayout)
        self.label = QLabel(msg, self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password = self.password_input.text().lower()

class Hashbrown:
    def __enter__(self):
        if self.build_mode:
            with open(get_path.go("secrets.json"), "w") as file:
                json.dump(self.decrypted_data, file)
                # file.write(self.decrypted_data)
            with open(get_path.go("serviceaccount.json"), "w") as file:
                json.dump(self.decrypted_data["jason"], file)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.build_mode:
            os.remove(get_path.go("secrets.json"))
            os.remove(get_path.go("serviceaccount.json"))

    def __init__(self, password=None, build_mode=False):
        self.build_mode = build_mode
        self.salt = b'`\xd8\xf8Dk>\x99\xa1\x1b\xc2n#\xc8P\xdde'  # os.urandom(16)

        self.encrypted_data = self.load_encrypted()

        self.decrypted_data = None
        self.kdf = None
        self.key = None
        self.cryptor = None

        if password:
            pass
        else:
            password_window = PasswordPopup("Enter Password")
            # no password supplied
            password = password_window.password
            # password = input("enter password: ")

        loop_lock = True
        while loop_lock:
            try:
                self.generate_cryptor(password.encode("ascii"))
                self.decrypt()
                loop_lock = False
            except cryptography.fernet.InvalidToken:
                print("Incorrect password, try again")
                password_window = PasswordPopup("Enter Password")
                password = password_window.password

    def generate_cryptor(self, password):
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=400000,
        )
        self.key = base64.urlsafe_b64encode(self.kdf.derive(password))
        self.cryptor = Fernet(self.key)

    def load_encrypted(self):
        with open(get_path.go("resources/secrets.json.enc"), "rb") as encrypted_file:
            data = encrypted_file.read()
        return data

    def write_encrypted(self):
        with open(get_path.go("resources/secrets.json.enc"), "wb") as encrypted_file:
            encrypted_file.write(self.encrypted_data)

    def encrypt(self, data=None):
        if not data:
            with open(get_path.go("secrets.json"), "rb") as decrypted_file:
                data = decrypted_file.read()
                try:
                    json.loads(data.decode("ascii"))
                except json.decoder.JSONDecodeError:
                    # badly formatted json
                    return -1
        else:
            data = json.dumps(data).encode('ascii')

        return self.cryptor.encrypt(data)

    def decrypt(self):
        if not self.encrypted_data:
            self.encrypted_data = self.load_encrypted()

        self.decrypted_data = json.loads(self.cryptor.decrypt(self.encrypted_data).decode("ascii"))
        # self.decrypted_data = self.cryptor.decrypt(self.encrypted_data).decode("ascii")

    def edit_contents(self):
        """
        To access file to edit, class must be instantiated in build_mode
        """
        loop_lock = True
        while loop_lock:
            action = input("Press 'Y' to confirm secrets update, press anything to cancel\n").upper()
            if action == "Y":
                # re-encrypt updated file
                self.encrypted_data = self.encrypt()
                if self.encrypted_data == -1:
                    print("Badly formatted json, please try again")
                    continue
                self.write_encrypted()
                loop_lock = False
            else:
                action = input(
                    "\nCancelling, press 'Y' to discard edits to secrets, press anything to cancel\n").upper()
                if action == "Y":
                    loop_lock = False

    def change_password(self, pwd=None):
        if not self.decrypted_data:
            self.decrypt()

        if not pwd:
            loop_lock = True
            while loop_lock:
                password_window1 = PasswordPopup("Enter new Password")
                password1 = password_window1.password
                password_window2 = PasswordPopup("Confirm new Password")
                password2 = password_window2.password
                if password1 == password2:
                    print("Passwords match, ", end="")
                    password = password1
                    loop_lock = False
                else:
                    print("Passwords don't match, try again")
        else:
            password = pwd

        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=400000,
        )
        self.key = base64.urlsafe_b64encode(self.kdf.derive(password.encode("ascii")))
        self.cryptor = Fernet(self.key)

        self.encrypted_data = self.encrypt(self.decrypted_data)
        self.write_encrypted()


""" To update the secrets, run this: """
if __name__ == "__main__":
    with Hashbrown(password="force", build_mode=True) as hashbrown:
        """ Contents editing: """
        # hashbrown.edit_contents()

        """ Password changing: """
        # hashbrown.change_password()