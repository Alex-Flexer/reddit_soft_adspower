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
from random import randint

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from login import slow_typing, rand_sleep, click

from log_windows import LogWindow

from re import findall
from keyring import get_password

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebdriver

from sys import path

path.insert(1, "functions")

from ads_driver import ads_driver
from db_funcs import get_reddit_accounts


WebDriver = ChromeWebdriver | FirefoxWebdriver

POST_URL = 'https://www.reddit.com/r/{subreddit}/submit/?type={type}'

PATTERN_ERROR_MESSAGE =\
    "div.items-baseline:nth-child(2) > r-form-validation-message:nth-child(1)"
PATTERN_FLAIR_BUTTON =\
    "#reddit-post-flair-button > span:nth-child(1) > span:nth-child(1)"
PATTERN_SUBMIT_BUTTON = "#submit-post-button"
PATTERN_TITLE_INPUT = "/html/body/shreddit-app/div[1]/div[1]/div/main/r-post-composer-form/section/div[1]/faceplate-tracker/faceplate-textarea-input"
PATTERN_ADD_FLAIR_BUTTON = "#post-flair-modal-apply-button"
PATTERN_FLAIR_SPANS =\
    "div.flex-col > div[name=flairId] > faceplate-radio-input > span"
PATTERN_SELECT_TYPE = "/html/body/shreddit-app/div[1]/div[1]/div/main/r-post-composer-form/r-post-type-select"


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


def post(
        mouse: ActionChains,
        driver: WebDriver,
        subreddit: str,
        file_path: str,
        title: str,
        flair: str | None = None
) -> tuple[str, bool]:
    copy_image_to_clipboard(file_path)

    post_url = POST_URL.format(subreddit=subreddit, type="IMAGE")
    driver.get(post_url)

    sleep(6)

    current_type = findall(r".*\?type=([A-Z]+)", driver.current_url)

    if "IMAGE" not in current_type:
        type_selection: list[WebElement] = driver.find_element(
            By.XPATH, PATTERN_SELECT_TYPE
        ).shadow_root.find_elements(
            By.CSS_SELECTOR, "faceplate-tracker"
        )

        choose_type_flag = False
        for type_element in type_selection:
            if "images" in type_element.text.lower():
                click(mouse, type_element)
                rand_sleep()
                choose_type_flag = True

        if not choose_type_flag:
            return "unable to use image type"

    current_type = findall(r".*\?type=([A-Z]+)", driver.current_url)
    if "IMAGE" not in current_type:
        return "unable to use image type"

    title_input_element = driver.find_element(
        By.XPATH, PATTERN_TITLE_INPUT)

    click(mouse, title_input_element)
    rand_sleep()

    slow_typing(title, mouse, 7, 0.9)
    rand_sleep()

    title_input_element.send_keys(Keys.CONTROL, 'v')

    sleep(4)

    flair_button_shadow_root: ShadowRoot = driver.find_element(
        By.CSS_SELECTOR, "#post-flair-modal").shadow_root
    flair_button_span: WebElement = flair_button_shadow_root.find_element(
        By.CSS_SELECTOR, PATTERN_FLAIR_BUTTON)

    flair_button_text: str = flair_button_span.text

    if flair is None and '*' in flair_button_text:
        return "expected flairs", False

    submit_button: WebElement = driver.find_element(
        By.CSS_SELECTOR, PATTERN_SUBMIT_BUTTON)

    if flair is not None:
        original_flair = flair.lower().strip()

        click(mouse, flair_button_span)
        sleep(5.82)

        faceplate_dialog_element_root = flair_button_shadow_root.find_element(
            By.CSS_SELECTOR, ".p-0")

        flairs_spans: list[WebElement] = \
            faceplate_dialog_element_root.find_elements(
                By.CSS_SELECTOR, PATTERN_FLAIR_SPANS)

        required_flair_element: WebElement | None = None

        for flair_span in flairs_spans:
            flair_text = flair_span.text.lower().strip()
            if original_flair == flair_text:
                required_flair_element = flair_span
                break

        if required_flair_element is None:
            return f"flair \"{flair}\" was not found", False

        click(mouse, required_flair_element)
        rand_sleep()

        add_flair_button = faceplate_dialog_element_root.find_element(
            By.CSS_SELECTOR, PATTERN_ADD_FLAIR_BUTTON)
        click(mouse, add_flair_button)
        rand_sleep()

    click(mouse, submit_button)
    rand_sleep()

    start_time = datetime.now()
    while datetime.now() - start_time < timedelta(seconds=20) and "submit" in driver.current_url:
        continue

    if "submit" in driver.current_url:
        error_message: list[WebElement] =\
            driver.find_element(By.CSS_SELECTOR, PATTERN_ERROR_MESSAGE).\
            shadow_root.find_elements(By.CSS_SELECTOR, "p.m-0")

        print(error_message[0])

        if len(error_message) != 0 and error_message[0].text != "":
            return error_message[0].text, False
        else:
            return "unknown post error", False
    else:
        return "was successfully posted", True


def big_post(
        logger: LogWindow,
        mouse: ActionChains,
        driver: WebDriver,
        subs_path: str,
        min_interval: int,
        max_interval: int
) -> None:

    for subdir in os.listdir(subs_path):
        sub_path = os.path.join(subs_path, subdir)

        subreddit_name = subdir

        good_subdir: bool = True
        if os.path.isdir(sub_path):
            used_path = os.path.join(sub_path, 'used')

            if not os.path.exists(used_path):
                os.makedirs(used_path)

            titles_path: str | None = None
            flairs_path: str | None = None

            titles: list[str] = []
            flairs: list[str] | None = None

            images_paths: list[str] = []

            for file in os.listdir(sub_path):
                file_path = os.path.join(sub_path, file)

                file_title: str = file.title().lower()

                if file_title == "titles.txt":
                    if len(titles) > 0:
                        logger.log_message(
                            subreddit_name, "file must contain only one titles file")
                        good_subdir = False
                        break

                    with open(file_path, 'r', encoding='utf-8') as f:
                        titles = f.read().strip().split('\n')
                        titles_path = file_path

                elif file_title == "flairs.txt":
                    if flairs is not None:
                        logger.log_message(
                            subreddit_name, "file must contain not more one flairs file")
                        good_subdir = False
                        break

                    with open(file_path, 'r', encoding='utf-8') as f:
                        flairs: list[str] = f.read().strip().split('\n')
                        flairs = [flair.strip() for flair in flairs]
                        flairs_path = file_path

                elif file_title.endswith((".jpg", ".png", ".jpeg")):
                    images_paths.append(file_path)

            if not good_subdir:
                continue

            flag = True

            if "" in titles:
                titles.remove("")
            if flairs is not None and "" in flairs:
                flairs.remove("")

            if len(images_paths) != len(titles):
                logger.log_message(
                    f"{subreddit_name}:", "amount of images do not match with amount of titles")
                flag = False

            if flairs is not None and len(images_paths) != len(flairs):
                logger.log_message(
                    f"{subreddit_name}:", "amount of images do not match with amount of flairs")
                flag = False

            if flairs is not None and len(titles) != len(flairs):
                logger.log_message(
                    f"{subreddit_name}:", "amount of titles do not match with amount of flairs")
                flag = False

            if titles_path is None:
                logger.log_message(
                    f"{subreddit_name}:", "there is no file \"titles.txt\"")
                flag = False

            print(len(images_paths), len(titles), len(flairs), images_paths, titles, flairs)

            if not flag:
                continue

            not_posted_titles: list[str] = []
            not_user_flairs: list[str] = []
            for ind, image_path in enumerate(images_paths):
                logger.log_message(
                    f"{subreddit_name}->{titles[ind]}: ", end="")
                try:
                    message, is_successfully_posted =\
                        post(mouse,
                             driver,
                             subreddit_name,
                             image_path,
                             titles[ind],
                             flairs[ind] if flairs else None)

                    logger.log_message(message)
                    if is_successfully_posted:
                        image_name = os.path.basename(image_path)
                        move(image_path, os.path.join(
                            sub_path, "used", image_name))
                    else:
                        not_posted_titles.append(titles[ind])
                        if flairs is not None:
                            not_user_flairs.append(flairs[ind])
                except Exception as e:
                    logger.log_message(str(e).lower())
                    not_posted_titles.append(titles[ind])
                    if flairs is not None:
                        not_user_flairs.append(flairs[ind])

                sleep(randint(min_interval, max_interval) * 60)

            with open(titles_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(not_posted_titles))

            if flairs is not None:
                with open(flairs_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(not_user_flairs))
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

        messagebox.showinfo("Info", f"Selected Adspower-ID: {reddit_account_ads_id}")
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


def tkinter_reddit_auto_post():
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
        min_interval = entry_min_interval.get()
        max_interval = entry_max_interval.get()

        if not all([subs_path, min_interval, max_interval]):
            messagebox.showerror("Error", "Fill in all input fields!")
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
                    min_interval,
                    max_interval
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

    tk.Button(
        root,
        text="Start Posting",
        font=("Modern No. 20", 18),
        command=start_big_post
    ).grid(row=4, column=1, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    tkinter_reddit_auto_post()
