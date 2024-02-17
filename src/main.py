
import asyncio

from services import driver_config, solve_captcha, parse_product_card, is_link_correct
from crud import get_links_list, get_or_create
from src.models import Link


async def parse_products() -> None:
    """Ф-ция выполняет сам парсинг страницы, используя driver"""
    driver = await driver_config()
    links = await get_links_list()
    try:

        for link_obj in links:
            #driver.get(f"{link_obj.link}&promo-type-filter=cheapest-as-gift")
            driver.get(f"{link_obj.link}&promo-type-filter=discount%2Cpromo-code%2Ccheapest-as-gift")

            # is_correct = await is_link_correct(driver)

            await solve_captcha(driver)
            await parse_product_card(driver, link_obj.discount)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


async def get_link_and_discount_from_user():
    """Получение ссылки и процент скидки от пользователя в консоли """

    while True:
        link = input("Введите ссылку (или 'exit' для завершения): ")

        if link.lower() == 'exit':
            await parse_products()
            break

        discount = input("Введите процент скидки: ")
        try:
            discount = int(discount)
        except ValueError:
            print("Ошибка: процент скидки должен быть числом.")
            continue

        await get_or_create(model=Link, link=link, discount=discount)


async def main():
    """Точка входа"""
    try:
        await parse_products()
        #await get_link_and_discount_from_user()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
