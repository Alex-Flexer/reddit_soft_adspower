from asyncio import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


RECIPIENT_TOKEN = "TMPYVBkVZj5pboTAW3VqsW29QMNq6F9Bwq"


async def check_transaction(amount: float, currency: str = "USDT") -> bool:
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://tronscan.org/#/address/{RECIPIENT_TOKEN}/transfers")

    await sleep(10)

    try:
        table_frame = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tab_data_list"))
        )
    except TimeoutException:
        print("Element was not found")
        driver.quit()
        return False

    table = table_frame.find_element(By.TAG_NAME, "tbody")
    driver.execute_script("arguments[0].scrollIntoView(true);", table)
    await sleep(1)

    lines = table.find_elements(By.TAG_NAME, "tr")
    for line in lines:
        cells = line.find_elements(By.TAG_NAME, "td")
        
        if len(cells) < 8:
            break

        transaction_age_str, value_str, currency_str =\
              cells[2].text, cells[6].text, cells[7].text

        if "day" in transaction_age_str:
            break

        value = float(value_str.replace(",", ""))

        if currency in currency_str and value == amount:
            driver.quit()
            return True

    driver.quit()
    return False
