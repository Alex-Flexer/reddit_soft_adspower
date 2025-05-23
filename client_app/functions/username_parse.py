from time import sleep

from selenium.webdriver.chrome.webdriver import WebDriver as chrome_webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as firefox_webdriver
import tkinter as tk

from selenium.webdriver.common.by import By
from log_windows import LogWindow

from driver import create_driver
from db_funcs import get_reddit_accounts
from tkinter import messagebox

user_email = None

from keyring import get_password

WebDriver = chrome_webdriver | firefox_webdriver

USERNAMES_PATTERN = ("span:nth-child(2) > span:nth-child(1) > span:nth-child(1) > div:nth-child(1) > "
                     "faceplate-hovercard:nth-child(1) > faceplate-tracker:nth-child(1) > a:nth-child(1)")


def parse_username(subreddit: str):
    driver = create_driver()
    log_window = LogWindow()
    driver.execute_script(f"window.scrollBy(0, 5);")

    post_url = rf'http://www.reddit.com/r/{subreddit}/new'
    sleep(2)

    driver.get(post_url)
    sleep(2)

    usernames_elements = driver.find_elements(By.CSS_SELECTOR, USERNAMES_PATTERN)
    usernames = {el.text.removeprefix('u/') for el in usernames_elements}

    if not usernames:
        log_window.log_message(f"No titles found on the subreddit '{subreddit}'")
        usernames = 'default username'

    log_window.log_message('\n'.join(usernames))


def tkinter_parse_username():

    global user_email
    user_email = get_password("user", "email")

    if user_email is None:
        messagebox.showerror('No accounts bought')
    accounts, msg = get_reddit_accounts(user_email)

    root = tk.Tk()
    root.title("Reddit Title Parser")

    tk.Label(root, text="Subreddit:",
             font=("Modern No. 20", 18)).grid(row=0, column=0, padx=10, pady=10)
    entry_subreddit = tk.Entry(root, width=30)
    entry_subreddit.grid(row=0, column=1, padx=10, pady=20)

    btn_parse = tk.Button(root, text="Parse Username",
                          command=lambda: parse_username(entry_subreddit.get()))
    btn_parse.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()
