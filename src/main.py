import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from fake_useragent import UserAgent
import time
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from sqlalchemy import Sequence, Row, RowMapping
from typing_extensions import Any

from services import driver_config, solve_captcha
from crud import add_link_to_db, get_links_list





async def parse_products(links) -> None:
    """Ф-ция выполняет сам парсинг страницы, используя driver"""
    driver = await driver_config()
    #&promo-type-filter=discount
    try:
        driver.get('https://captcha-api.yandex.ru/demo')
        await solve_captcha(driver)
        # for link_obj in links:
        #     driver.get(f"{link_obj.link}&promo-type-filter=discount")
        #     await solve_captcha()
        #     # name = driver.find_element(By.CLASS_NAME, '_1E10J _2o124 _1zh3_')
        #     # print(name.text)
        #
        #     time.sleep(30)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


async def products_finder():
    """Ф-ция вызывает ф-цию get_links_list для получения ссылок и далее вызывает ф-цию parse_products для парсинга карточек товара"""
    links = await get_links_list()
    #print(links)
    products = await parse_products(links)


async def get_link_and_discount_from_user():
    """Получение ссылки и процент скидки от пользователя в консоли """

    while True:
        link = input("Введите ссылку (или 'exit' для завершения): ")

        if link.lower() == 'exit':
            await products_finder()
            break
        discount = input("Введите процент скидки: ")

        try:
            discount = int(discount)
        except ValueError:
            print("Ошибка: процент скидки должен быть числом.")
            continue
        await add_link_to_db(link=link, discount=discount)


async def main():
    """Точка входа"""
    try:
        await products_finder()
        #await get_link_and_discount_from_user()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
