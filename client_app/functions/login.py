from time import sleep
from datetime import datetime, timedelta
from random import random, choice, uniform
from string import ascii_letters as letters

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebdriver


WebDriver = ChromeWebdriver | FirefoxWebdriver


def click(mouse: ActionChains, element: WebElement) -> None:
    mouse.move_to_element(element).perform()
    rand_sleep()
    mouse.click().perform()


def slow_typing(text: str, mouse: ActionChains, speed: int = 0, accuracy: float = 1.0) -> None:
    def send_key(key: str) -> None:
        nonlocal mouse, speed
        mouse.send_keys(key).perform()
        sleep(uniform(0.05, 1) / (1 + speed / 10))

    for key in text:
        if random() > accuracy:
            random_key = choice(letters)
            send_key(random_key)
            send_key(Keys.BACKSPACE)

        send_key(key)


def rand_sleep() -> None:
    sleep(uniform(0.1, 1))


def _login(mouse: ActionChains, driver: WebDriver, username: str, password: str, speed: int = 0, accuracy: float = 1.0) -> bool:
    driver.get("https://www.reddit.com/login/")

    sleep(3)

    login_input = driver.find_element(By.ID, "login-username")
    password_input = driver.find_element(By.ID, "login-password")

    click(mouse, login_input)
    rand_sleep()

    slow_typing(username, mouse, speed, accuracy)
    rand_sleep()

    click(mouse, password_input)
    rand_sleep()

    slow_typing(password, mouse, speed, accuracy)
    rand_sleep()

    mouse.send_keys(Keys.ENTER).perform()

    sleep(10)

    start_time = datetime.now()
    while datetime.now() - start_time < timedelta(seconds=20) and "www.reddit.com/login/" in driver.current_url:
        continue

    return "www.reddit.com/login/" not in driver.current_url


def login(*args, **kwargs):
    for _ in range(5):
        try:
            result = _login(*args, **kwargs)
        except Exception:
            pass
        else:
            if result:
                return True
        sleep(20)

    return False
