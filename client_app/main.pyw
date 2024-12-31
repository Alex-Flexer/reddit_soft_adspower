from tkinter import messagebox

from keyring import get_password, set_password
from requests import post
from json import dumps

from sys import path

path.insert(1, "tkinter_app")

from tkinter_app import start_registration, create_window


def check_user(email, password, token):
    data = dumps({"email": email, "password": password, "token": token})
    json = None
    try:
        response = post(
            "http://thekarmamaster.com/check/user-credentials/", data=data)
        json = response.json()
    finally:
        return json


def main():
    email = get_password("user", "email")
    password = get_password("user", "password")
    token = get_password("user", "token")

    if not email or not password or not token:
        start_registration()
    else:
        response_json = check_user(email, password, token)
        if response_json is None:
            messagebox.showerror("Error", "Network error")
        elif not response_json["result"]:
            if response_json["message"] ==\
                    "Subscription expired or was not completed":
                messagebox.showerror("Error", response_json["message"])
            else:
                start_registration()
        else:
            if "token" in response_json:
                set_password("user", "token", response_json["token"])
            create_window()


if __name__ == "__main__":
    main()
