from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def test_fakenodo_connection():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f'{host}/fakenodo/api')

        time.sleep(3)

        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text

            assert "You have successfully connected to Fakenodo" in body_text

        except NoSuchElementException:
            raise AssertionError("El cuerpo de la página no contiene el mensaje esperado.")

    finally:

        close_driver(driver)

