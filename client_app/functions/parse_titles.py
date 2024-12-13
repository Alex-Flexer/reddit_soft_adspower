from time import sleep
import random
import re

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as chrome_webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as firefox_webdriver

import tkinter as tk

from log_windows import LogWindow


WebDriver = chrome_webdriver | firefox_webdriver


def get_random_int(max_value):
    return random.randint(0, max_value - 1)


def parse_titles(subreddit: str) -> str:
    driver = webdriver.Chrome()
    log_window = LogWindow()

    post_url1 = f'http://www.reddit.com/r/{subreddit}/new'
    sleep(3)

    driver.get(post_url1)
    sleep(3)

    html = driver.page_source
    titles = re.findall(r'aria-label="([^"]*)"', html)
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               "]+", flags=re.UNICODE)
    to_remove = {
        'Home', 'Notifications', 'Close dialog', 'Shreddit QR', 'Google play', 'App store',
        'Community actions', 'Post distinguished by admin', 'Post distinguished by moderator',
        'Locked post', 'Sticked post', 'Archived post', 'Reddit resources', 'Primary', 'Community information',
        'Edit user flair', "'", '"', 'New rule announcement.',
        f'r/{subreddit} - Join the official amihot Discord server ', 'Join the official amihot Discord server ',
        f'r/{subreddit} - New rule announcement.', '[', ']'
    }
    filtered_titles = [title for title in titles if title not in to_remove]
    filtered_titles = emoji_pattern.sub(r'', str(filtered_titles))
    if not filtered_titles:
        log_window.log_message(f"No titles found on the subreddit '{subreddit}'")
        filtered_titles = 'default title'

    return filtered_titles


def tkinter_parse_titles():
    root = tk.Tk()
    root.title("Reddit Title Parser")

    tk.Label(root, text="Subreddit:").grid(row=0, column=0, padx=10, pady=10)
    entry_subreddit = tk.Entry(root)
    entry_subreddit.grid(row=0, column=1, padx=10, pady=10)

    btn_parse = tk.Button(root, text="Parse Titles", command=lambda: parse_titles(entry_subreddit.get()))
    btn_parse.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == '__main__':
    tkinter_parse_titles()
