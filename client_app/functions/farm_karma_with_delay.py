import tkinter as tk
from tkinter import messagebox
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebdriver
from log_windows import LogWindow
from threading import Thread
from keyring import get_password
from db_funcs import get_reddit_accounts, get_proxy
from proxy import driver_proxy
from datetime import datetime, timedelta
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from tkinter import ttk
import schedule
from farm_carma import farm_carma

WebDriver = ChromeWebdriver | FirefoxWebdriver


def run_schedule(start_time: datetime, func, *args, **kwargs):
    def run_func(func, *args, **kwargs):
        func(*args, **kwargs)
        return schedule.CancelJob

    start_time_str = start_time.strftime("%H:%M")
    schedule.every().day.at(start_time_str).do(run_func, func, *args, **kwargs)

    while True:
        schedule.run_pending()
        sleep(30)


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


def tkinter_reddit_farm_with_delay():
    global reddit_account_email, reddit_account_password

    def update_status():
        if reddit_account_email:
            label_selected_account.config(text=f"Selected Account: {
                                          reddit_account_email}", fg="green")
        else:
            label_selected_account.config(text="No account selected", fg="red")

    def start_farming():
        if not reddit_account_email:
            messagebox.showerror("Error", "Please select an account first!")
            return

        start_time_str = start_time_entry.get()
        end_time_str = end_time_entry.get()
        subreddit_name = subreddit_entry.get()

        if not all([start_time_str, end_time_str, subreddit_name]):
            messagebox.showerror("Error", "Fill in all inputs fields!")
            return

        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format! Use HH:MM.")
            return

        now = datetime.now().time()
        if end_time <= start_time:
            end_time += timedelta(days=1)

        if now >= start_time or now >= end_time:
            messagebox.showerror("Error", "Invalid time interval!")
            return

        end_time_full = datetime.combine(datetime.today(), end_time)

        def run_farming():
            proxy, err = get_proxy(reddit_account_email)
            if err is not None:
                messagebox.showerror("Error", err)
                return

            driver = driver_proxy(**proxy)
            mouse = ActionChains(driver)
            logger = LogWindow()

            farming_thread =\
                Thread(
                    target=farm_carma,
                    args=(
                        logger,
                        mouse,
                        driver,
                        end_time_full,
                        reddit_account_email,
                        reddit_account_password,
                        subreddit_name
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
        run_schedule(start_time, run_farming)

    root = tk.Tk()
    root.title("Reddit Karma Farmer")

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

    label_selected_account = tk.Label(
        root,
        text="No account selected",
        font=("Modern No. 20", 18),
        fg="red"
    )
    label_selected_account.grid(row=0, column=2, padx=10, pady=10)

    tk.Label(
        root,
        text="Start Time (HH:MM):",
        font=("Modern No. 20", 14)
    ).grid(row=1, column=0, padx=10, pady=10, sticky="e")

    start_time_entry = ttk.Entry(root, font=("Modern No. 20", 14))
    start_time_entry.grid(row=1, column=1, padx=10, pady=10)
    start_time_entry.insert(0, "00:00")

    tk.Label(
        root,
        text="End Time (HH:MM):",
        font=("Modern No. 20", 14)
    ).grid(row=2, column=0, padx=10, pady=10, sticky="e")

    end_time_entry = ttk.Entry(root, font=("Modern No. 20", 14))
    end_time_entry.grid(row=2, column=1, padx=10, pady=10)
    end_time_entry.insert(0, "00:00")

    tk.Label(
        root,
        text="Subreddit name:",
        font=("Modern No. 20", 14)
    ).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    subreddit_entry = ttk.Entry(root, font=("Modern No. 20", 14))
    subreddit_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Button(
        root,
        text="Start Farming",
        font=("Modern No. 20", 18),
        command=start_farming
    ).grid(row=4, column=1, padx=10, pady=10)

    root.mainloop()
