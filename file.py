from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import time


proxy_user = 'zavalishinn26'
proxy_password = 'uKvcZHash5'
proxy_host = '45.85.204.182'
proxy_port = '50100'


def driver_proxy(proxy_host, proxy_port, proxy_user, proxy_password):
    proxy_options = {
        'proxy': {
            'http': f'http://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}',
            'https': f'http://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    o = Options()
    o.add_argument("--headless")
    driver = webdriver.Chrome(seleniumwire_options=proxy_options, options=o)

    return driver


driver = driver_proxy(proxy_host, proxy_port, proxy_user, proxy_password)
driver.get('https://2ip.ru')
time.sleep(10)
print(driver.page_source)
driver.quit()
