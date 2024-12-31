import tkinter as tk
from tkinter import filedialog, messagebox
from time import sleep
from datetime import datetime, timedelta
import os

from threading import Thread
from shutil import move

import win32clipboard as clip
import win32con
from io import BytesIO
from PIL import Image

from selenium.webdriver.common.action_chains import ActionChains

from log_windows import LogWindow

from keyring import get_password

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebdriver

from parse_titles import parse_titles
from sys import path

path.insert(1, "functions")

from ads_driver import ads_driver
from db_funcs import get_reddit_accounts
from auto_post import post


WebDriver = ChromeWebdriver | FirefoxWebdriver


reddit_account_ads_id = None
user_email = None


def copy_image_to_clipboard(image_path: str):
    image = Image.open(image_path)
    output = BytesIO()
    image.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardData(win32con.CF_DIB, data)
    clip.CloseClipboard()


def big_post(
        logger: LogWindow,
        mouse: ActionChains,
        driver: WebDriver,
        subs_path: str,
) -> None:

    for subdir in os.listdir(subs_path):
        sub_path = os.path.join(subs_path, subdir)

        subreddit_name = subdir.split('=')[0]

        if os.path.isdir(sub_path):
            used_path = os.path.join(sub_path, 'used')

            if not os.path.exists(used_path):
                os.makedirs(used_path)


            images_paths: list[str] = []

            for file in os.listdir(sub_path):
                file_path = os.path.join(sub_path, file)

                file_title: str = file.title().lower()

                if file_title.endswith((".jpg", ".png", ".jpeg")):
                    images_paths.append(file_path)


            not_posted_titles: list[str] = []
            not_user_flairs: list[str] = []

            sub_title = parse_titles(subreddit_name, reddit_account_ads_id)
            flair = subdir.split('=')[1]
            if flair == '':
                flair = None

            for image_path in images_paths:
                logger.log_message(
                    f"{subreddit_name}->{sub_title}: ", end="")
                try:
                    message, is_successfully_posted =\
                        post(mouse,
                             driver,
                             subreddit_name,
                             image_path,
                             parse_titles(subreddit_name),
                             flair if flair else None)

                    logger.log_message(message)
                    if is_successfully_posted:
                        image_name = os.path.basename(image_path)
                        move(image_path, os.path.join(
                            sub_path, "used", image_name))
                    else:
                        not_posted_titles.append(sub_title)
                        if flair is not None:
                            not_user_flairs.append(flair)
                except Exception as e:
                    logger.log_message(str(e).lower())


        logger.log_message(f"Posting {subreddit_name} if finished")
    driver.quit()
    logger.log_message("Posting is finished!")


def choose_email_window(update_status_callback):
    """Open a window for choosing an account."""
    global user_email
    user_email = get_password("user", "email")

    if user_email is None:
        return
    accounts, msg = get_reddit_accounts(user_email)

    if accounts is None:
        messagebox.showerror("Error", msg)
        return

    def select_ads_id(ads_id):
        global reddit_account_ads_id
        reddit_account_ads_id = ads_id

        update_status_callback()
        email_window.destroy()

    email_window = tk.Tk()
    email_window.title("Choose Adspower-ID")
    tk.Label(
        email_window,
        text="Choose an Adspower-ID:",
        font=("Modern No. 20", 14)
    ).pack(pady=10)

    for account in accounts:
        tk.Button(
            email_window,
            text=account,
            font=("Modern No. 20", 12),
            command=lambda a=account: select_ads_id(a)
        ).pack(pady=5)

    email_window.mainloop()


def tkinter_reddit_auto_post_auto_title():
    root = tk.Tk()

    def update_status():
        if reddit_account_ads_id:
            entry_ads_id.config(
                text=f"Selected Account: {reddit_account_ads_id}",
                fg="green"
            )
        else:
            entry_ads_id.config(text="No account selected", fg="red")

    def select_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry_folder.delete(0, tk.END)
            entry_folder.insert(0, folder_selected)

    def start_big_post():
        nonlocal root

        subs_path = entry_folder.get()


        if not all([subs_path]):
            messagebox.showerror("Error", "Fill in all input fields!")
            return

        if not (os.path.exists(subs_path) and os.path.isdir(subs_path)):
            messagebox.showerror("Error", "Invalid folder path!")
            return

        ads_id = reddit_account_ads_id
        driver = ads_driver(ads_id)
        mouse = ActionChains(driver)
        logger: LogWindow = LogWindow()
        logger.log_message("Logger is successfully initialized")

        poster_thread =\
            Thread(
                target=big_post,
                args=(
                    logger,
                    mouse,
                    driver,
                    subs_path,
                ),
                daemon=True
            )
        poster_thread.start()

        def on_close():
            logger.root.destroy()
            driver.quit()
            exit(0)

        logger.run(on_close)

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

    entry_ads_id =\
        tk.Label(
            root,
            text="No account selected",
            font=("Modern No. 20", 18),
            fg="red"
        )

    entry_ads_id.grid(row=0, column=2, padx=10, pady=10)


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

    tk.Button(
        root,
        text="Start Posting",
        font=("Modern No. 20", 18),
        command=start_big_post
    ).grid(row=4, column=1, padx=10, pady=10)

    root.mainloop()

