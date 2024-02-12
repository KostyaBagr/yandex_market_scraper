import time
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import asyncio

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
    await asyncio.sleep(2)  # Добавим задержку перед началом работы
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe')))
    print(iframe, 'iframe')
    # Переключаемся на iframe
    driver.switch_to.frame(iframe)

    # Находим чекбокс капчи и кликаем на него
    checkbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#checkbox')))
    print(checkbox, 'checkbox')
    checkbox.click()

    # Ждем, пока капча обработается
    await asyncio.sleep(5)
    print("Капча решена успешно!")
