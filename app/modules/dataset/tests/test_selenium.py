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


def test_upload_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Log in
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Count initial datasets
        initial_datasets = count_datasets(driver, host)

        # Open the upload dataset page
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        # Fill in basic dataset information
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "title")))
        driver.find_element(By.NAME, "title").send_keys("Title")
        driver.find_element(By.NAME, "desc").send_keys("Description")
        driver.find_element(By.NAME, "tags").send_keys("tag1,tag2")

        # Add authors
        for i in range(2):
            add_author_button = driver.find_element(By.ID, "add_author")
            add_author_button.click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, f"authors-{i}-name"))
            )
            driver.find_element(By.NAME, f"authors-{i}-name").send_keys(f"Author{i}")
            driver.find_element(By.NAME, f"authors-{i}-affiliation").send_keys(f"Club{i}")
            if i == 0:  # Only add ORCID for the first author
                driver.find_element(By.NAME, f"authors-{i}-orcid").send_keys("0000-0000-0000-0000")

        # Upload files
        file_paths = [
            os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl"),
            os.path.abspath("app/modules/dataset/uvl_examples/file2.uvl"),
        ]
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        for file_path in file_paths:
            dropzone.send_keys(file_path)
            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, "dz-success-mark"), "")  # Confirm file upload
            )

        # Add author to UVL models
        show_button = driver.find_element(By.ID, "0_button")
        show_button.click()
        add_author_uvl_button = driver.find_element(By.ID, "0_form_authors_button")
        add_author_uvl_button.click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "feature_models-0-authors-2-name"))
        )
        driver.find_element(By.NAME, "feature_models-0-authors-2-name").send_keys("Author3")
        driver.find_element(By.NAME, "feature_models-0-authors-2-affiliation").send_keys("Club3")

        # Agree to terms and upload
        check = driver.find_element(By.ID, "agreeCheckbox")
        check.click()
        upload_btn = driver.find_element(By.ID, "upload_button")
        upload_btn.click()

        # Wait for redirection
        WebDriverWait(driver, 10).until(EC.url_to_be(f"{host}/dataset/list"))

        # Verify the dataset was uploaded
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Dataset count mismatch! Upload failed."

        print("Test passed!")

    except Exception as e:
        print(f"Test failed: {e}")
        raise

    finally:
        # Always close the driver
        close_driver(driver)


# Call the test function
test_upload_dataset()


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
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Verificar el botón de calificación
        rate_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-target='#ratingModal']"))
        )
        rate_button.click()

        # Asegurarse de que el modal esté visible
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ratingModal")))

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


def test_rate_without_login():
    driver = initialize_driver()

    try:
        # Configurar la URL del dataset
        host = get_host_for_selenium_testing()
        dataset_id = 4  # Ajusta al ID del dataset que necesitas probar
        dataset_url = f"{host}/dataset/{dataset_id}/rate"

        # Navegar a la página del dataset (sin iniciar sesión)
        driver.get(dataset_url)

        # Asegurarse de que la página esté completamente cargada
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Hacer clic en el botón de enviar calificación
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        send_button.click()

        # Esperar a que ocurra la redirección
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        # Verificar que se redirigió a la página de inicio de sesión
        assert "login" in driver.current_url, "No se redirigió a la página de inicio de sesión"
        assert "next=%2Fdataset%2F4%2Frate" in driver.current_url, "El parámetro 'next' no es correcto"

        print("Prueba exitosa: Redirección a inicio de sesión confirmada.")

    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
        driver.save_screenshot("login_redirect_error.png")
    finally:

        driver.quit()


test_rate_without_login()
