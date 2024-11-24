from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pytest


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_homepage(driver):
    driver.get("http://localhost:5000/fakenodo")
    assert "Fakenodo" in driver.title


def test_test_connection(driver):
    driver.get("http://localhost:5000/fakenodo/api")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "You have successfully connected to Fakenodo" in body_text


def test_create_deposition(driver):
    driver.get("http://localhost:5000/fakenodo")
    driver.find_element(By.NAME, "uvl_filename").send_keys("Test File")
    driver.find_element(By.NAME, "title").send_keys("Test Title")
    driver.find_element(By.NAME, "desc").send_keys("This is a test description.")
    driver.find_element(By.ID, "submit").click()
    success_message = driver.find_element(By.CLASS_NAME, "alert-success").text
    assert "Fakenodo deposition created" in success_message


def test_delete_deposition(driver):
    deposition_id = 123
    driver.get(f"http://localhost:5000/fakenodo/api/{deposition_id}")
    delete_button = driver.find_element(By.ID, "delete")
    delete_button.click()
    time.sleep(1)
    confirm_message = driver.find_element(By.CLASS_NAME, "alert-success").text
    assert "successfully deleted a deposition" in confirm_message


def test_publish_deposition(driver):
    deposition_id = 123
    driver.get(f"http://localhost:5000/fakenodo/api/{deposition_id}/actions/publish")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "You have successfully published a deposition" in body_text


def test_get_deposition(driver):
    deposition_id = 123
    driver.get(f"http://localhost:5000/fakenodo/api/{deposition_id}")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "10.5072/fakenodo.123456" in body_text
