from seleniumwire import webdriver
from seleniumwire.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


def driver_proxy(host, port, user, password) -> Chrome:
    proxy_options = {
        'proxy': {
            'http': f'http://{user}:{password}@{host}:{port}',
            'https': f'http://{user}:{password}@{host}:{port}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(
        seleniumwire_options=proxy_options,
        options=options)

    return driver
