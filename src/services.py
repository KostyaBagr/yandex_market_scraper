import time
import re
from collections import namedtuple
import asyncio
from itertools import zip_longest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from src.crud import get_or_create_product


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

    while True:
        await asyncio.sleep(2)

        product_blocks = driver.find_elements(By.CLASS_NAME, '_3yjG2')
        print(product_blocks)
        for product_block in product_blocks:
            try:
                # Получаем ссылку из названия товара
                link = product_block.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print(link)
                name = product_block.find_element(By.CLASS_NAME, '_1E10J').text.strip()
                print(name)
                green_price = product_block.find_element(By.CLASS_NAME, '_1stjo').text.strip()
                print(green_price)
                discount = product_block.find_element(By.CLASS_NAME, '_3ZKoP').text.strip()
                print(discount)
                promotion = product_block.find_element(By.CLASS_NAME, 'ko6OZ').text.strip()
                print(promotion)
                promocode = product_block.find_element(By.CLASS_NAME, '_2X3hM').text.strip()
                print(promocode)
            except NoSuchElementException:
                pass
            # Определяем регулярное выражение для извлечения числовых значений
            # regex = re.compile('[^0-9]')
            # green_price = regex.sub('', green_price)
            # discount = regex.sub('', discount)
            #
            # if int(discount) >= link_discount:  # Если скидка соответствует критериям
            #     data = {
            #         "name": name,
            #         "green_price": green_price,
            #         "discount": discount,
            #         "red_price": "",
            #         "link": link,  # Используем полученную ссылку
            #         "promotion": promotion,
            #         "promocode": promocode
            #     }
            #     print(data)
            #     await get_or_create_product(data=data)



        try:
            pagination = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div/div[4]/div/div/div[1]/div/div/div[5]/div/div/div/div/div/div/div/div[7]/div/div/div[1]/div/button')
            actions = ActionChains(driver)
            actions.move_to_element(pagination).click().perform()
            await asyncio.sleep(2)
        except NoSuchElementException:
            print("Достигнут конец товаров")
            break


async def is_link_correct(driver: webdriver):
    """Функция проверяет ссылку на корректность"""
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_1He5n')))
        return True

    except Exception as ex:
        return False


async def calculate_final_price(data: dict):
    # data = price, promotion (2=1)=None, promocode(-20%)=None
    price = int(data['price'])

    promotion_price = (price * data['promotion'][1]) // data['promotion'][0] if data['promotion'] else None
    promocode_price = price - ((data['promocode'] / 100) * price) if data['promocode'] else None
    total_price = price - (promocode_price + promotion_price)
    total_percent = (total_price // price) * 100
