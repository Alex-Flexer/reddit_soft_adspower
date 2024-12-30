from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from seleniumwire.webdriver import Chrome
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys


def ads_driver(ads_id) -> Chrome:
    ads_id = ads_id
    open_url = "http://local.adspower.net:50325/api/v1/browser/start?user_id=" + ads_id

    resp = requests.get(open_url).json()
    if resp["code"] != 0:
        print(resp["msg"])
        print("please check ads_id")
        sys.exit()

    chrome_driver = resp['data']["webdriver"]
    service = Service(executable_path=chrome_driver)
    chrome_options = Options()

    chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
    driver = webdriver.Chrome(options=chrome_options, service=service)

    return driver
