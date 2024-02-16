import time
import re
from collections import namedtuple
import asyncio
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
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        await asyncio.sleep(2)

        names = driver.find_elements(By.CLASS_NAME, '_1E10J')
        green_prices = driver.find_elements(By.CLASS_NAME, '_1stjo') or driver.find_elements(By.CSS_SELECTOR,
                                                                                             '[data-auto="price-value"]')
        discount_values = driver.find_elements(By.CLASS_NAME, '_3ZKoP')
        detail_links = driver.find_elements(By.CLASS_NAME, 'egKyN')
        #romotions = driver.find_elements(By.CLASS_NAME, 'ko6OZ')

        for name, price, discount, link in zip(names, green_prices, discount_values, detail_links):
            name = name.text
            price = price.text
            discount = discount.text
            link = link.get_attribute('href')

            promotions = [i.text for i in driver.find_elements(By.CLASS_NAME, 'ko6OZ')]

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
                print(f'скидка похдодит товар - {name}')
                await get_or_create_product(product_price=int(price), data=data)
                # await add_product_to_db(data) #refactor: вместо добавления я должен получать ИЛИ добавлять
        try:
            pagination = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div/div[4]/div/div/div[1]/div/div/div[5]/div/div/div/div/div/div/div/div[7]/div/div/div[1]/div/button')
            print(pagination.text, 'pagination')
            actions = ActionChains(driver)
            actions.move_to_element(pagination).click().perform()
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
