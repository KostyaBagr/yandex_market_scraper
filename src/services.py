import re
import aiohttp
import asyncio
import os
import urllib.parse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from dotenv import load_dotenv
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from src.crud import get_or_create_product

load_dotenv()


async def driver_config():
    """WebDriver config"""

    options = webdriver.ChromeOptions()
    user_agent = UserAgent()

    options.add_argument(f"user-agent={user_agent.chrome}")
    options.add_argument('--headless')
    options.add_argument("--disable-blink-features=AutomationControlled")  # отлючение видмости webdriver

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


async def solve_captcha(driver: webdriver):
    """Ф-ция решает капчу на сайте"""
    wait = WebDriverWait(driver, 5)
    try:
        wait.until(EC.presence_of_element_located((By.ID, 'js-button'))).click()
        await asyncio.sleep(2)
        print('Капча успешно пройдена')
        return True
    except Exception as e:
        print('Капча не найдена')
        return False


async def send_tg_message(data: dict):
    """Ф-ция формирует уведомление для тг и отправляет в группу, используя api телеграм"""
    print('tg message!')
    data = await calculate_final_price(data)
    message = f"Цена снизилась!\n\n" \
              f"Название - {data.get('name')}\n" \
              f"Цена - {data.get('price')} руб\n" \
              f"Акция|Промокод - {data.get('promotion') if data.get('promotion') else 'Акции нет'}|{data.get('promocode') if data.get('promocode') else 'Промокода нет'}\n" \
              f"Окончательный процент скидки - {data.get('total_percent') if data.get('total_percent') else 'Скидка не изменилась'}\n" \
              f"Ссылка - {data.get('link')}"
    encoded_message = urllib.parse.quote_plus(message)

    async with aiohttp.ClientSession() as session:
        await session.get(
            f'https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage?chat_id=-100{os.getenv("CHAT_ID")}&text={encoded_message}')


async def parse_product_card(driver: webdriver, link_discount: int):
    """Ф-ция забирает данные с карточки товара"""

    while True:

        product_blocks = driver.find_elements(By.CLASS_NAME, '_3yjG2')

        for product_block in product_blocks:
            link = name = promotion = promocode = None

            try:
                price_element = product_block.find_element(By.CSS_SELECTOR, '[data-auto="price-value"]')
                price = price_element.text.strip()
                discount = product_block.find_element(By.CLASS_NAME, '_1oI3I').text.strip()
            except NoSuchElementException:
                try:
                    price_element = product_block.find_element(By.CLASS_NAME, '_1stjo')
                    price = price_element.text.strip()
                    discount = product_block.find_element(By.CLASS_NAME, '_3ZKoP').text.strip()
                except NoSuchElementException as e:
                    print("Не удалось найти цену и скидку:", e)
                    continue

            if product_block.find_elements(By.CLASS_NAME, '_3SIKw'):
                promotion = product_block.find_element(By.CLASS_NAME, '_3SIKw').text.strip()
                print(promotion, 'акция')
            if product_block.find_element(By.TAG_NAME, 'a'):
                link = product_block.find_element(By.TAG_NAME, 'a').get_attribute('href')

            if product_block.find_element(By.CLASS_NAME, '_1E10J'):
                name = product_block.find_element(By.CLASS_NAME, '_1E10J').text.strip()

            if product_block.find_elements(By.CLASS_NAME, '_2X3hM'):
                promocode = product_block.find_element(By.CLASS_NAME, '_2X3hM').text.strip()

            regex = re.compile('[^0-9]')
            price = int(regex.sub('', price)) if price else None
            discount = int(regex.sub('', discount))
            promocode = int(regex.sub('', promocode)) if promocode else None
            promotion = regex.sub('', promotion) if promotion else None

            if discount >= link_discount:  # Если скидка соответствует критериям
                data = {
                    "name": name,
                    "price": price,
                    "discount": discount,
                    "link": link,
                    "promotion": promotion,
                    "promocode": promocode
                }
                print("Скидка подходит")

                if await get_or_create_product(data=data, name=data['name']):
                    await send_tg_message(data)

        try:
            pagination = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div/div[4]/div/div/div[1]/div/div/div[5]/div/div/div/div/div/div/div/div[7]/div/div/div[1]/div/button')
            actions = ActionChains(driver)
            actions.move_to_element(pagination).click().perform()
            await asyncio.sleep(2)
        except NoSuchElementException:
            print("Парсинг данной ссылки закончился")
            break


async def calculate_final_price(data: dict):
    """Функция подсчитывает окончательную цену со всеми акциями и промокодами """

    if not data['promotion'] and not data['promocode']:
        # если нет ни акции, ни промокода
        return data

    elif data['promotion'] and data[
        'promocode']:  # нахожу цену за один товар при наличии акции (3=2) и далее вычитаю процент промокода(-20%) из полученного числа

        promotion_price = (
                (data['price'] * int(data['promotion'][1])) / int(data['promotion'][0]))  # находим цену за 1 товар
        total_price = promotion_price - (
                promotion_price * data['promocode']) / 100  # из цены этого товара вычитаем процент купона

    elif data['promocode']:  # если есть промокод (-20%), то вычитаем из базовый цены этот процент

        total_price = data['price'] - (data['price'] * data['promocode'] / 100)

    elif data['promotion']:  # если есть акция(3=2), то находим цену за один товар

        total_price = (data['price'] * int(data['promotion'][1])) / int(data['promotion'][0])

    else:
        return False

    total_percent = (total_price / data['price']) * 100  # сверяем получившийся процент и процент ссылки
    if total_percent >= data['discount']:
        data['price'], data['total_percent'] = round(total_price), total_percent
        return data


async def is_link_correct(driver: webdriver):
    """Функция проверяет ссылку на корректность"""
    wait = WebDriverWait(driver, 5)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_1He5n')))
        return True

    except Exception as ex:
        return False
