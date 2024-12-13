import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets


def test_download_all_datasets():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)
        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Open the download all datasets page
        driver.get(f"{host}/dataset/download/all")
        wait_for_page_to_load(driver)

        # Verify that the "Download all dataset" link is present in the navigation bar
        download_link = driver.find_element(By.LINK_TEXT, "Download all dataset")
        assert download_link.is_displayed(), "Download all dataset link is not displayed in the navigation bar"

        print("Test passed!")

    finally:

        # Close the browser
        close_driver(driver)


test_download_all_datasets()


