import time
import re
import asyncio

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from src.crud import get_or_create_product
from src.main import parse_products


async def driver_config():
    """WebDriver config"""

    options = webdriver.ChromeOptions()
    user_agent = UserAgent()

    options.add_argument(f"user-agent={user_agent.chrome}")
    options.add_argument("--disable-blink-features=AutomationControlled")  # отлючение видмости webdriver
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


async def solve_captcha(driver: webdriver):
    """Ф-ция решает капчу на сайте"""
    wait = WebDriverWait(driver, 5)
    try:
        wait.until(EC.presence_of_element_located((By.ID, 'js-button'))).click()
        await asyncio.sleep(3)
        print('true')
        return True
    except Exception as e:
        print('false')
        return False


async def parse_product_card(driver: webdriver, link_discount: int):
    """Ф-ция забирает данные с карточки товара"""

    pagination = driver.find_element(By.CLASS_NAME, 'B-RPM')

    max_tab = max([int(char) for char in pagination.text if char.isdigit()])
    curr_tab = 1

    while curr_tab <= max_tab:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        await asyncio.sleep(2)

        name = driver.find_elements(By.CLASS_NAME, '_1E10J')
        old_price = driver.find_elements(By.CLASS_NAME, '_8-sD9')
        discount_val = driver.find_elements(By.CLASS_NAME, '_3ZKoP')
        detail_link = driver.find_elements(By.CLASS_NAME, 'egKyN')

        for name, price, discount, link in zip(name, old_price, discount_val, detail_link):
            name = name.text
            price = price.text
            discount = discount.text
            link = link.get_attribute('href')

            regex = re.compile('[^0-9]')
            price = regex.sub('', price)
            discount = regex.sub('', discount)

            if int(discount) >= link_discount:  # если скидка у товара больше, либо равняется скидке, указанной в ссылке, то сохраняем в бд
                data = {
                    "name": name,
                    "link": link,
                    "price": price,
                    "discount": discount
                }
                print('скидка похдодит ')
                await get_or_create_product(product_price=int(price), data=data)
                # await add_product_to_db(data) #refactor: вместо добавления я должен получать ИЛИ добавлять

        curr_tab += 1

        # if driver.find_element(By.CLASS_NAME, '_2fBJ5'):
        #     break


async def is_link_correct(driver: webdriver):
    """Функция проверяет ссылку на корректность"""
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_1He5n')))
        return True

    except Exception as ex:
        return False
