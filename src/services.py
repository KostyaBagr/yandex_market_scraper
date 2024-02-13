import time
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import asyncio

from src.crud import add_product_to_db


async def driver_config():
    """WebDriver config"""

    options = webdriver.ChromeOptions()
    user_agent = UserAgent()

    options.add_argument(f"user-agent={user_agent.chrome}")
    options.add_argument("--disable-blink-features=AutomationControlled")  # отлючение видмости webdriver
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


async def solve_captcha(driver):
    """Ф-ция решает капчу на сайте"""
    wait = WebDriverWait(driver, 10)
    try:
        is_captcha = wait.until(EC.presence_of_element_located((By.ID, 'js-button'))).click()
        await asyncio.sleep(5)
        return True
    except Exception as e:
        return False


async def parse_product_card(driver):
    """Ф-ция забирает данные с карточки товара"""
    name = driver.find_elements(By.CLASS_NAME, '_1E10J')
    old_price = driver.find_elements(By.CLASS_NAME, '_8-sD9')
    discount_val = driver.find_elements(By.CLASS_NAME, '_3ZKoP')
    detail_link = driver.find_elements(By.CLASS_NAME, 'egKyN')

    for name, price, discount, link in zip(name, old_price, discount_val, detail_link):
        name = name.text
        price = price.text[14:]
        discount = discount.text
        link = link.get_attribute('href')

        regex = re.compile('[^0-9]')
        price = regex.sub('', price)
        discount = regex.sub('', discount)

        data = {
            "name": name,
            "link": link,
            "price": price,
            "discount": discount
        }
        await add_product_to_db(data)