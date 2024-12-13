from time import sleep
from random import random, choice, uniform
from string import ascii_letters as letters

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
