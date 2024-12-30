import tkinter as tk
from tkinter import messagebox
from requests import ConnectionError, post
from json import dumps
from keyring import set_password as set_secret_value, get_password
from main_func_app import create_window


user_email: str | None = None
user_password: str | None = None

root: None | tk.Tk = None


def save_credentials() -> None:
    token = update_token(user_email)
    if token is None:
        return
    set_secret_value("user", "email", user_email)
    set_secret_value("user", "password", user_password)
    set_secret_value("user", "token", token)


def get_user_email():
    return get_password("user", "email")


def update_token(email: str) -> None | str:
    data = dumps({"email": email})
    try:
        response = post("http://thekarmamaster.com/update/user-token/", data=data)
        json = response.json()
    except ConnectionError:
        messagebox.showerror("Error", "Network error")
    else:
        if not json["result"]:
            messagebox.showerror("Error", json["message"])
        else:
            return json["token"]


def start_registration():
    root = tk.Tk()
    root.title("Registration")

    tk.Label(root, text="Tg-nickname:", font=("Modern No. 20", 18)).grid(row=0, column=0, padx=10, pady=5)
    entry_email = tk.Entry(root)
    entry_email.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Password:", font=("Modern No. 20", 18)).grid(row=1, column=0, padx=10, pady=5)
    entry_password = tk.Entry(root, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    def submit_login_password():
        global user_email, user_password
        nonlocal entry_password, entry_email

        email = entry_email.get()
        password = entry_password.get()

        if not email or not password:
            messagebox.showerror("Error", "Please fill the required fields")
            return

        response_json = authenticate_user(email, password)

        if response_json is None:
            messagebox.showerror("Error", "Network error")

        elif response_json["result"]:
            user_email = email
            user_password = password

            root.destroy()
            request_code()

        else:
            messagebox.showerror("Error", response_json["message"])

    tk.Button(root, text="Enter", font=("Modern No. 20", 18), command=submit_login_password).grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()


def request_code():
    global root

    root = tk.Tk()
    root.title("Confirm Email Code")

    tk.Label(root, text="Enter your confirmation code:", font=("Modern No. 20", 18)).grid(row=0, column=0, padx=10, pady=5)
    entry_code = tk.Entry(root)
    entry_code.grid(row=0, column=1, padx=10, pady=5)

    def verify_code():
        entered_code = entry_code.get()

        data = dumps({"email": user_email, "code": entered_code})
        try:
            response = post("http://thekarmamaster.com/confirm/email-code", data=data)
            response_json = response.json()
        except ConnectionError:
            messagebox.showerror("Error", "Network error")
        else:
            if response_json["result"]:
                messagebox.showinfo("Success", "Your email code is successfully confirmed!")
                save_credentials()
                root.destroy()
                create_window()
            else:
                messagebox.showerror("Error", response_json["message"])

    tk.Button(root, text="Confirm", command=verify_code).grid(row=1, column=0, columnspan=2, pady=10)

    root.mainloop()


def authenticate_user(email: str, password: str) -> dict | None:
    data = dumps({"email": email, "password": password})
    json = None

    try:
        response = post("http://thekarmamaster.com/login/user", data=data)
        json = response.json()
    finally:
        return json


if __name__ == '__main__':
    start_registration()
