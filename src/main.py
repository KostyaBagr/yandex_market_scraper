import requests

from selenium import webdriver
from fake_useragent import UserAgent
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def driver_config():
    """WebDriver config"""

    options = webdriver.ChromeOptions()
    user_agent = UserAgent()

    options.add_argument(f"user-agent={user_agent.chrome}")
    options.add_argument("--disable-blink-features=AutomationControlled")  # отлючение видмости webdriver
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def parse():
    print("Вы в фунции parse")
    time.sleep(5)


def get_link_and_discount_from_user():
    """Получение ссылки и процент скидки от пользователя в консоли """

    while True:
        link = input("Введите ссылку (или 'exit' для завершения): ")

        if link.lower() == 'exit':
            parse()
            break
        discount = input("Введите процент скидки: ")

        try:
            discount = float(discount)
        except ValueError:
            print("Ошибка: процент скидки должен быть числом.")
            continue

        print(f"Ссылка: {link}, Скидка: {discount}%")


def main():
    """Точка входа"""
    # driver = driver_config()
    try:
        get_link_and_discount_from_user()
    except Exception as e:
        print(e)
    finally:
        pass
        # driver.close()
        # driver.quit()


if __name__ == "__main__":
    main()
