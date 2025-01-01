from time import sleep
import re
from random import choice
from selenium.webdriver.chrome.webdriver import WebDriver as chrome_webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as firefox_webdriver
from ads_driver import ads_driver
import tkinter as tk

from driver import create_driver
from log_windows import LogWindow


WebDriver = chrome_webdriver | firefox_webdriver


def parse_titles_list(subreddit: str):
    driver = create_driver()
    log_window = LogWindow()
    driver.execute_script(f"window.scrollBy(0, 5);")

    post_url = f'http://www.reddit.com/r/{subreddit}/new'

    driver.get(post_url)
    sleep(2)

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
        f'r/{subreddit} - New rule announcement.', 'Back', 'Close', 'Promotion', 'Stickied post'
    }
    filtered_titles = [title for title in titles if title not in to_remove]
    for i, title in enumerate(filtered_titles):
        filtered_titles[i] = emoji_pattern.sub(r'', title)

    if not filtered_titles:
        log_window.log_message(f"No titles found on the subreddit '{subreddit}'")
        filtered_titles = 'default title'

    log_window.log_message('\n'.join(filtered_titles))


def parse_titles(subreddit: str, ads_id) -> str:
    driver = ads_driver(ads_id)
    log_window = LogWindow()

    post_url = f'http://www.reddit.com/r/{subreddit}/new'

    driver.get(post_url)
    sleep(2)

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
        f'r/{subreddit} - New rule announcement.', 'Back', 'Close', 'Promotion', 'Stickied post', 'Create Post'
    }
    filtered_titles = [title for title in titles if title not in to_remove]
    for i, title in enumerate(filtered_titles):
        filtered_titles[i] = emoji_pattern.sub(r'', title)

    if not filtered_titles:
        log_window.log_message(f"No titles found on the subreddit '{subreddit}'")
        filtered_titles = 'default title'

    return choice(filtered_titles)


def tkinter_parse_titles():
    root = tk.Tk()
    root.title("Reddit Title Parser")

    tk.Label(root, text="Subreddit:").grid(row=0, column=0, padx=10, pady=10)
    entry_subreddit = tk.Entry(root)
    entry_subreddit.grid(row=0, column=1, padx=10, pady=10)

    btn_parse = tk.Button(root, text="Parse Titles", command=lambda: parse_titles_list(entry_subreddit.get()))
    btn_parse.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()
