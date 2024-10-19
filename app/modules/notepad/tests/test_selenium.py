import pytest
import time
import json
from selenium import webdriver

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def test_createnotepad():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}/login')
        time.sleep(2)
        driver.set_window_size(912, 1011)
        driver.find_element(By.ID, "email").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "submit").click()
        time.sleep(2)
        driver.get(f"{host}/notepad/create")
        time.sleep(2)
        driver.find_element(By.ID, "title").click()
        driver.find_element(By.ID, "title").send_keys("n1")
        driver.find_element(By.ID, "body").click()
        driver.find_element(By.ID, "body").send_keys("n1")
        driver.find_element(By.ID, "submit").click()
    finally:

        # Close the browser
        close_driver(driver)


if __name__ == "__main__":
    test_createnotepad()