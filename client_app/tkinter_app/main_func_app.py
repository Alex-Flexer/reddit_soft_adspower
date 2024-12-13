from keyring import get_password
import tkinter as tk
from tkinter import messagebox
from multiprocessing import Process
import sys

sys.path.insert(1, 'functions')

from big_post_with_delay import tkinter_reddit_big_post_with_delay
from farm_karma_with_delay import tkinter_reddit_farm_with_delay
from image_editing import uniq_tkinter
from converters import tkinter_converters
from big_post import tkinter_reddit_big_post
from farm_carma import tkinter_reddit_farm
from db_funcs import add_account


def create_window():
    root = tk.Tk()
    root.title("Reddit Soft")

    root.geometry("400x400")

    root.configure(bg="#f0f0f0")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame, bg="#f0f0f0")
    scrollbar = tk.Scrollbar(
        main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    button_config = {
        "font": ("Modern No. 20", 14, "bold"),
        "bg": "black",
        "fg": "white",
        "activebackground": "#45a049",
        "activeforeground": "black",
        "bd": 3,
        "relief": "raised",
        "width": 28,
        "height": 2
    }

    label = tk.Label(scrollable_frame, text="Choose a Function",
                     font=("Modern No. 20", 18), bg="#f0f0f0")
    label.pack(pady=10)

    buttons = [
        ("Add Reddit-Account", add_reddit_account),
        ("Farm Karma", tkinter_reddit_farm),
        ("Post Auto", tkinter_reddit_big_post),
        ("Farm Karma with delay", tkinter_reddit_farm_with_delay),
        ("Post Auto with delay", tkinter_reddit_big_post_with_delay),
        ("Uniqueize photo or video", uniq_tkinter),
        ("Converters", tkinter_converters),
    ]

    def start_process(func):
        Process(target=func, daemon=True).start()

    for text, func in buttons:
        button = tk.Button(
            scrollable_frame,
            text=text,
            command=lambda f=func: start_process(f),
            **button_config
        )

        button.pack(pady=10)

    root.mainloop()


def add_reddit_account():
    login_window = tk.Tk()
    login_window.title("User Credentials")

    tk.Label(login_window, text="Email:").grid(
        row=0, column=0, padx=10, pady=5)
    entry_login = tk.Entry(login_window)
    entry_login.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(login_window, text="Password:").grid(
        row=1, column=0, padx=10, pady=5)
    entry_reddit_password = tk.Entry(login_window, show="*")
    entry_reddit_password.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(login_window, text="Proxy Host:").grid(
        row=2, column=0, padx=10, pady=5)
    entry_host = tk.Entry(login_window)
    entry_host.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(login_window, text="Proxy Port:").grid(
        row=3, column=0, padx=10, pady=5)
    entry_port = tk.Entry(login_window)
    entry_port.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(login_window, text="Proxy User:").grid(
        row=4, column=0, padx=10, pady=5)
    entry_user = tk.Entry(login_window)
    entry_user.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(login_window, text="Proxy Password:").grid(
        row=5, column=0, padx=10, pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=5, column=1, padx=10, pady=5)

    def submit_account_credentials():
        login = entry_login.get()
        password = entry_reddit_password.get()
        proxy_host = entry_host.get()
        proxy_port = entry_port.get()
        proxy_user = entry_user.get()
        proxy_password = entry_password.get()

        if not all([login, password, proxy_host, proxy_port, proxy_user, proxy_password]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        user_email = get_password("user", "email")
        add_account(user_email, login, password, proxy_host,
                    proxy_port, proxy_user, proxy_password)

        login_window.destroy()

    tk.Button(login_window, text="Submit", command=submit_account_credentials).grid(
        row=6, column=0, columnspan=2, pady=10)
    login_window.mainloop()


if __name__ == "__main__":
    create_window()
