import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


def test_login_with_invalid_credentials():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()

        # Open login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Input invalid credentials
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("invalid_user@example.com")
        password_field.send_keys("wrong_password")
        password_field.send_keys(Keys.RETURN)

        # Wait for page to load and check for error message
        wait_for_page_to_load(driver)
        error_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Usuario o contraseña incorrectos" in error_message, "Error message not displayed!"

        print("Test passed: Login with invalid credentials")
    finally:
        close_driver(driver)

test_login_with_invalid_credentials()

def test_rating_without_authentication():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()

        # Open dataset page (replace DOI with a valid one for the test)
        doi = "10.1234/example-doi"
        driver.get(f"{host}/doi/{doi}/")
        wait_for_page_to_load(driver)

        # Try to open rating modal
        try:
            rating_modal_button = driver.find_element(By.ID, "ratingModalButton")
            rating_modal_button.click()
        except Exception as e:
            print(f"Rating modal button not found: {e}")
            assert False, "Rating modal button is not displayed!"

        # Check if the login prompt appears
        modal_message = driver.find_element(By.CLASS_NAME, "modal-body").text
        assert "Debes iniciar sesión para calificar este dataset." in modal_message, \
            "Login prompt not displayed for unauthenticated user"

        print("Test passed: Rating attempt without authentication")
    finally:
        close_driver(driver)


def test_valid_rating_with_authenticated_user():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()

        # Login as a valid user
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Open dataset page (replace DOI with a valid one for the test)
        doi = "10.1234/example-doi"
        driver.get(f"{host}/doi/{doi}/")
        wait_for_page_to_load(driver)

        # Open rating modal
        rating_modal_button = driver.find_element(By.ID, "ratingModalButton")
        rating_modal_button.click()

        # Select a rating (e.g., 4 stars)
        stars = driver.find_elements(By.CLASS_NAME, "fa-star")
        for star in stars:
            if star.get_attribute("data-score") == "4":
                star.click()
                break

        # Submit the rating
        submit_button = driver.find_element(By.CLASS_NAME, "btn-primary")
        submit_button.click()
        wait_for_page_to_load(driver)

        # Check for success message
        flash_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Gracias por calificar" in flash_message, "Rating not submitted successfully"

        print("Test passed: Valid rating submission with authenticated user")
    finally:
        close_driver(driver)


def test_duplicate_rating_updates_score():
    driver = initialize_driver()
    try:
        host = get_host_for_selenium_testing()

        # Login as a valid user
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Open dataset page (replace DOI with a valid one for the test)
        doi = "10.1234/dataset1"
        driver.get(f"{host}/doi/{doi}/")
        wait_for_page_to_load(driver)

        # Open rating modal
        rating_modal_button = driver.find_element(By.ID, "ratingModalButton")
        rating_modal_button.click()

        # Submit a rating (e.g., 3 stars)
        stars = driver.find_elements(By.CLASS_NAME, "fa-star")
        for star in stars:
            if star.get_attribute("data-score") == "3":
                star.click()
                break
        submit_button = driver.find_element(By.CLASS_NAME, "btn-primary")
        submit_button.click()
        wait_for_page_to_load(driver)

        # Submit a different rating (e.g., 5 stars)
        rating_modal_button.click()
        stars = driver.find_elements(By.CLASS_NAME, "fa-star")
        for star in stars:
            if star.get_attribute("data-score") == "5":
                star.click()
                break
        submit_button.click()
        wait_for_page_to_load(driver)

        # Check for updated score
        flash_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Gracias por calificar" in flash_message, "Rating update failed"

        print("Test passed: Duplicate rating updates score")
    finally:
        close_driver(driver)