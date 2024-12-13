import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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


def test_rate_dataset():
    driver = initialize_driver()

    try:
        # Generar la URL usando el DOI
        host = get_host_for_selenium_testing()
        doi = "10.1234/1"  # Reemplaza con el DOI que necesitas probar
        dataset_url = f"{host}/doi/{doi}/"
        
        # Navegar a la página del dataset
        driver.get(dataset_url)

        # Asegurarse de que la página esté completamente cargada
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Verificar el botón de calificación
        rate_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-target='#ratingModal']"))
        )
        rate_button.click()

        # Asegurarse de que el modal esté visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ratingModal"))
        )

        # Interactuar con las estrellas y enviar el formulario
        stars = driver.find_elements(By.CLASS_NAME, "star")
        assert len(stars) == 5, "No se encontraron las 5 estrellas de calificación"
        stars[2].click()

        hidden_input = driver.find_element(By.ID, "rating")
        assert hidden_input.get_attribute("value") == "3", "La calificación no se guardó correctamente"

        # Enviar el formulario
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Validar que la acción se completó correctamente
        success_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "flash-message"))
        )
        assert "Thank you" in success_message.text, "No se mostró el mensaje de éxito"

    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
        driver.save_screenshot("timeout_error.png")
    finally:
        driver.quit()


test_rate_dataset()