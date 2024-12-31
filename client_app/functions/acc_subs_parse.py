from selenium.webdriver.chrome.webdriver import WebDriver as chrome_webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as firefox_webdriver

from selenium.webdriver.common.by import By

import tkinter as tk

import re

from time import sleep

from selenium.webdriver import Chrome

from log_windows import LogWindow

WebDriver = chrome_webdriver | firefox_webdriver

TITLES_PATTERN = ('span:nth-child(2) > span:nth-child(1) > span:nth-child(1) > shreddit-async-loader:nth-child(1)'
                  ' > faceplate-hovercard:nth-child(1) > a:nth-child(1) > span:nth-child(2)')

def parse_acc_subs(username: str) -> str:
    driver = Chrome()
    log_window = LogWindow()
    post_url = f'https://www.reddit.com/user/{username}/submitted/'
    sleep(2)

    driver.get(post_url)
    sleep(2)

    titles_elements = driver.find_elements(By.CSS_SELECTOR, TITLES_PATTERN)
    titles = {el.text.removeprefix('u/') for el in titles_elements}

    if not titles:
        log_window.log_message(f"No subs found in acc'{username}'")
        filtered_titles = 'default sub'

    print('\n'.join(titles))

def tkinter_parse_acc_subs():
    root = tk.Tk()
    root.title("Reddit Account Subs Parser")

    tk.Label(
        root,
        text="Enter Username for Subs:",
        font=("Modern No. 20", 18)
    ).grid(row=1, column=0, padx=10, pady=10)

    ads_id = tk.Entry(root, width=30)
    ads_id.grid(row=1, column=1, padx=10, pady=10)

    btn_parse = tk.Button(root, text="Parse Subs", command=lambda: parse_acc_subs(ads_id.get()))
    btn_parse.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()
