import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver

# Función para esperar a que se cargue la página
def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

# Función para contar el número de datasets
def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets

# Inicialización del driver con el chromedriver descargado manualmente
def initialize_driver():
    # Configura el path a tu chromedriver descargado
    service = Service("/usr/local/bin/chromedriver")  # Ruta al chromedriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Si lo deseas en modo headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Test para verificar la descarga de todos los datasets
def test_download_all_datasets():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Abrir la página de login
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Encontrar el campo de email y contraseña, e ingresarlos
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Enviar el formulario
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Abrir la página para descargar todos los datasets
        driver.get(f"{host}/dataset/download/all")
        wait_for_page_to_load(driver)

        # Verificar que el link "Download all dataset" está presente en la barra de navegación
        download_link = driver.find_element(By.LINK_TEXT, "Download all dataset")
        assert download_link.is_displayed(), "Download all dataset link is not displayed in the navigation bar"
        print("Test passed!")

    finally:
        # Cerrar el navegador
        close_driver(driver)

# Llamar a la función del test
test_download_all_datasets()

# Test para subir un dataset
def test_upload_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Abrir la página de login
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Encontrar el campo de email y contraseña, e ingresarlos
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Enviar el formulario
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Contar los datasets iniciales
        initial_datasets = count_datasets(driver, host)

        # Abrir la página para subir un dataset
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        # Llenar la información básica y el modelo UVL
        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Title")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.send_keys("Description")
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("tag1,tag2")

        # Agregar dos autores
        add_author_button = driver.find_element(By.ID, "add_author")
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field0 = driver.find_element(By.NAME, "authors-0-name")
        name_field0.send_keys("Author0")
        affiliation_field0 = driver.find_element(By.NAME, "authors-0-affiliation")
        affiliation_field0.send_keys("Club0")
        orcid_field0 = driver.find_element(By.NAME, "authors-0-orcid")
        orcid_field0.send_keys("0000-0000-0000-0000")

        name_field1 = driver.find_element(By.NAME, "authors-1-name")
        name_field1.send_keys("Author1")
        affiliation_field1 = driver.find_element(By.NAME, "authors-1-affiliation")
        affiliation_field1.send_keys("Club1")

        # Obtener las rutas absolutas de los archivos
        file1_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        file2_path = os.path.abspath("app/modules/dataset/uvl_examples/file2.uvl")

        # Subir el primer archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file1_path)
        wait_for_page_to_load(driver)

        # Subir el segundo archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file2_path)
        wait_for_page_to_load(driver)

        # Agregar autores en los modelos UVL
        show_button = driver.find_element(By.ID, "0_button")
        show_button.send_keys(Keys.RETURN)
        add_author_uvl_button = driver.find_element(By.ID, "0_form_authors_button")
        add_author_uvl_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field = driver.find_element(By.NAME, "feature_models-0-authors-2-name")
        name_field.send_keys("Author3")
        affiliation_field = driver.find_element(By.NAME, "feature_models-0-authors-2-affiliation")
        affiliation_field.send_keys("Club3")

        # Aceptar los términos y enviar el formulario
        check = driver.find_element(By.ID, "agreeCheckbox")
        check.send_keys(Keys.SPACE)
        wait_for_page_to_load(driver)

        upload_btn = driver.find_element(By.ID, "upload_button")
        upload_btn.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        time.sleep(2)  # Espera forzada

        assert driver.current_url == f"{host}/dataset/list", "Test failed!"

        # Contar los datasets finales
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Test failed!"

        print("Test passed!")

    finally:
        # Cerrar el navegador
        close_driver(driver)

# Llamar a la función del test
test_upload_dataset()
