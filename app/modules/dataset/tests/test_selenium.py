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
        # Abrir la página del dataset
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/dataset/1")  # Asegúrate de reemplazar con la URL correcta
        wait_for_page_to_load(driver)

        # Hacer clic en el botón para abrir el modal
        rate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-target='#ratingModal']"))
        )
        rate_button.click()

        # Esperar que el modal esté visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ratingModal"))
        )

        # Interactuar con las estrellas para calificar
        stars = driver.find_elements(By.CLASS_NAME, "star")
        assert len(stars) == 5, "No se encontraron las 5 estrellas de calificación"

        # Simular clic en la tercera estrella (por ejemplo)
        stars[2].click()

        # Verificar que el valor oculto se actualiza correctamente
        hidden_input = driver.find_element(By.ID, "rating")
        assert hidden_input.get_attribute("value") == "3", "La calificación seleccionada no es correcta"

        # Hacer clic en "Enviar"
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Validar que el formulario fue enviado correctamente
        # Por ejemplo, buscando un mensaje de confirmación o redirección
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "Thank you" in success_message.text, "No se mostró el mensaje de éxito esperado"

    except TimeoutException as e:
        print("Timeout occurred:", e)
        driver.save_screenshot("test_rate_dataset_timeout.png")
        raise

    except AssertionError as e:
        print("Assertion failed:", e)
        driver.save_screenshot("test_rate_dataset_assertion_failed.png")
        raise

    finally:
        close_driver(driver)


test_rate_dataset()