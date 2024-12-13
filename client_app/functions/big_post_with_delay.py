import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import os
from threading import Thread
from log_windows import LogWindow
from selenium.webdriver import ActionChains
from keyring import get_password

from big_post import big_post
from proxy import driver_proxy
from farm_karma_with_delay import run_schedule
from db_funcs import get_reddit_accounts, get_proxy

user_email = None
reddit_account_email = None
reddit_account_password = ""


def choose_email_window(update_status_callback):
    global user_email
    user_email = get_password("user", "email")

    if user_email is None:
        return
    accounts, msg = get_reddit_accounts(user_email)

    if accounts is None:
        messagebox.showerror("Error", msg)
        return

    def select_email(email, password):
        global reddit_account_email, reddit_account_password
        print(email, password)
        reddit_account_email = email
        reddit_account_password = password
        messagebox.showinfo("Info", f"Selected Email: {reddit_account_email}")
        update_status_callback()
        email_window.destroy()

    email_window = tk.Tk()
    email_window.title("Choose Email")
    tk.Label(email_window, text="Choose an Email:",
             font=("Modern No. 20", 14)).pack(pady=10)

    for account in accounts:
        tk.Button(
            email_window,
            text=account['email'],
            font=("Modern No. 20", 12),
            command=lambda e=account["email"], p=account["password"]: select_email(
                e, p)
        ).pack(pady=5)

    email_window.mainloop()


def tkinter_reddit_big_post_with_delay():
    global user_email

    def update_status():
        if reddit_account_email:
            label_selected_account.config(text=f"Selected Account: {
                                          reddit_account_email}", fg="green")
        else:
            label_selected_account.config(text="No account selected", fg="red")

    def select_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry_folder.delete(0, tk.END)
            entry_folder.insert(0, folder_selected)

    def start_big_post():
        if not reddit_account_email:
            messagebox.showerror("Error", "Please select an account first!")
            return

        subs_path = entry_folder.get()
        start_time_str = entry_time.get()
        min_interval = entry_min_interval.get()
        max_interval = entry_max_interval.get()

        if not all([subs_path, start_big_post, min_interval, max_interval]):
            messagebox.showerror("Error", "Fill in all input fields")
            return

        if not (os.path.exists(subs_path) and os.path.isdir(subs_path)):
            messagebox.showerror("Error", "Invalid folder path!")
            return

        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format! Use HH:MM.")
            return

        try:
            min_interval = int(min_interval)
            max_interval = int(max_interval)
        except ValueError:
            messagebox.showerror("Error", "Interval must be integer!")
            return

        if max_interval < min_interval:
            messagebox.showerror("Error", "Maximum time interval must be greater than minimum time interval!")
            return

        if start_time < datetime.now().time():
            start_time += timedelta(days=1)

        def run_posting():
            proxy, err = get_proxy(reddit_account_email)
            if err is not None:
                messagebox.showerror("Error", err)
                return

            driver = driver_proxy(**proxy)
            mouse = ActionChains(driver)
            logger = LogWindow()
            logger.log_message("Logger is successfully initialized")

            farming_thread =\
                Thread(
                    target=big_post,
                    args=(
                        logger,
                        mouse,
                        driver,
                        subs_path,
                        reddit_account_email,
                        reddit_account_password,
                        min_interval,
                        max_interval
                    ),
                    daemon=True
                )
            farming_thread.start()

            def on_close():
                logger.root.destroy()
                driver.quit()
                exit(0)

            logger.run(on_close)

        root.destroy()
        run_schedule(start_time, run_posting)

    root = tk.Tk()
    root.title("Reddit Big Poster")

    tk.Label(
        root,
        text="Select Account:",
        font=("Modern No. 20", 18)
    ).grid(row=0, column=0, padx=10, pady=10)

    tk.Button(
        root,
        text="Choose Account",
        font=("Modern No. 20", 18),
        command=lambda: choose_email_window(update_status)
    ).grid(row=0, column=1, padx=10, pady=10)

    label_selected_account =\
        tk.Label(root,
                 text="No account selected",
                 font=("Modern No. 20", 18),
                 fg="red"
                 )
    label_selected_account.grid(row=0, column=2, padx=10, pady=10)

    tk.Label(
        root,
        text="Select subs folder:",
        font=("Modern No. 20", 18)
    ).grid(row=1, column=0, padx=10, pady=10)

    entry_folder = tk.Entry(root, width=50)
    entry_folder.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(
        root,
        text="Browse",
        font=("Modern No. 20", 18),
        command=select_folder
    ).grid(row=1, column=2, padx=10, pady=10)

    valid = root.register(lambda text: text.isdigit())
    tk.Label(
        root,
        text="Minimum time interval (mins):",
        font=("Modern No. 20", 14)
    ).grid(row=2, column=0, padx=10, pady=10, sticky="e")

    entry_min_interval = tk.Entry(
        root,
        font=("Modern No. 20", 14),
        validate="key",
        validatecommand=(valid, "%S")
    )

    entry_min_interval.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(
        root,
        text="Maximum time interval (mins):",
        font=("Modern No. 20", 14)
    ).grid(row=3, column=0, padx=10, pady=10, sticky="e")

    entry_max_interval = tk.Entry(
        root,
        font=("Modern No. 20", 14),
        validate="key",
        validatecommand=(valid, "%S")
    )
    entry_max_interval.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(
        root,
        text="Start Time (HH:MM):",
        font=("Modern No. 20", 18)
    ).grid(row=4, column=0, padx=10, pady=10)

    entry_time = tk.Entry(root, width=10)
    entry_time.grid(row=4, column=1, padx=10, pady=10)
    entry_time.insert(0, "00:00")

    tk.Button(
        root,
        text="Start Posting",
        font=("Modern No. 20", 18),
        command=start_big_post
    ).grid(row=5, column=1, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    p = get_proxy("alexandr.flexer@gmail.com")
    print(p)
