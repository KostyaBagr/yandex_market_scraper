import asyncio

from services import driver_config, solve_captcha, parse_product_card
from crud import get_links_list, get_or_create
from src.models import Link

from multiprocessing import Process, Semaphore


async def parse_products(link_obj) -> None:
    """Ф-ция выполняет сам парсинг страницы, используя driver"""

    driver = await driver_config()
    try:

        driver.get(f"{link_obj.link}&promo-type-filter=discount%2Cpromo-code%2Ccheapest-as-gift")
        await solve_captcha(driver)
        await parse_product_card(driver, link_obj.discount)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def start_parsing(semaphore: Semaphore, link: Link):
    """Функция для запуска парсинга в отдельном процессе"""
    while True:
        with semaphore:
            asyncio.run(parse_products(link))


async def multiprocessing_conf():
    """Ф-ция выстраивает логику мультипроцессинга. Создаем список с процессами, который будет заполнен объектами Link,
    с помощью семафоры ограничиваем кол-во процессов"""
    links = await get_links_list()
    processes = []
    semaphore = Semaphore(4)
    for link_obj in links:
        process = Process(target=start_parsing, args=(semaphore, link_obj,))
        process.start()
        processes.append(process)

    # Дожидаемся завершения всех процессов
    for process in processes:
        process.join()


async def get_link_and_discount_from_user():
    """Получение ссылки и процент скидки от пользователя в консоли """

    while True:
        link = input("Введите ссылку (или 'exit' для завершения): ")

        if link.lower() == 'exit':
            print('Вы вышли из режима добавления ссылок, начинается парсинг')
            await multiprocessing_conf()
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
        await get_link_and_discount_from_user()  # Получаем ссылки от пользователя
    except Exception as e:
        print(e)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
