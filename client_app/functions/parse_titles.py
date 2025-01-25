from time import sleep
import re
from random import choice
from threading import Thread

from selenium.webdriver.chrome.webdriver import WebDriver as chrome_webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as firefox_webdriver
from selenium.webdriver.common.by import By

import tkinter as tk

from driver import create_driver
from log_windows import LogWindow


WebDriver = chrome_webdriver | firefox_webdriver
from db_funcs import get_reddit_accounts
from tkinter import messagebox

user_email = None

from keyring import get_password

def get_titles(subreddit: str):
    driver = create_driver()

    post_url = f'http://www.reddit.com/r/{subreddit}/new'

    driver.get(post_url)
    sleep(2)

    driver.execute_script(
        '''
        let el = document.querySelector("shreddit-async-loader.theme-beta");
        if (el) { el.remove(); }
        ''')
    sleep(2)

    driver.execute_script(f"window.scrollBy(0, 700);")
    sleep(3)

    titles_elements = driver.find_elements(By.CSS_SELECTOR, "a.block")
    titles = [element.text.strip() for element in titles_elements]
    titles = [title for title in titles if title]
    return titles


def parse_titles(subreddit: str, logger: LogWindow):
    logger.log_message("Parsing titles is started...")

    titles = get_titles(subreddit)

    if not titles:
        logger.log_message(f"No titles found on the subreddit '{subreddit}'")
    else:
        logger.log_message("Titles:")
        logger.log_message('\n\n'.join(titles))


def get_random_title(subreddit: str, logger: LogWindow) -> str:
    titles = get_titles(subreddit)
    if not titles:
        logger.log_message(f"No titles found on the subreddit '{subreddit}'")
    return choice(titles)


def tkinter_parse_titles():

    global user_email
    user_email = get_password("user", "email")

    if user_email is None:
        messagebox.showerror('No accounts bought')
    accounts, msg = get_reddit_accounts(user_email)

    def parse_titles_wrapper(subreddit: str, logger: LogWindow):
        root.destroy()
        thr = Thread(target=parse_titles, args=(subreddit, logger), daemon=True)
        thr.start()
        logger.run()

    root = tk.Tk()
    root.title("Reddit Title Parser")

    tk.Label(root, text="Subreddit:").grid(row=0, column=0, padx=10, pady=10)
    entry_subreddit = tk.Entry(root)
    entry_subreddit.grid(row=0, column=1, padx=10, pady=10)

    logger = LogWindow()

    btn_parse = tk.Button(
        root,
        text="Parse Titles",
        command=lambda: parse_titles_wrapper(entry_subreddit.get(), logger)
    )
    btn_parse.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    titles = get_titles("nft")
    print(titles)