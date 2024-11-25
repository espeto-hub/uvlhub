from selenium import webdriver
from selenium.webdriver.common.by import By
import pytest


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_test_connection(driver):
    driver.get("http://localhost:5000/fakenodo/api")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "You have successfully connected to Fakenodo" in body_text
