# Generated by Selenium IDE
from selenium.webdriver.common.by import By
from app.modules.dataset.tests.test_selenium import wait_for_page_to_load
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def test_checkdatasetuser():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f'{host}')
        wait_for_page_to_load(driver)
        driver.set_window_size(1854, 1048)
        driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        driver.find_element(By.LINK_TEXT, "Doe, Jane").click()
        driver.find_element(By.LINK_TEXT, "Sample dataset 2").click()
        print("Test passed successfully")
    finally:
        close_driver(driver)


# Call the test function
test_checkdatasetuser()