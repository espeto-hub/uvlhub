import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FakenodoTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup Chrome WebDriver
        cls.driver = webdriver.Chrome(executable_path='/path/to/chromedriver')  # Asegúrate de poner el path correcto
        cls.driver.get("http://127.0.0.1:5000")  # La URL de tu aplicación Flask local
        cls.driver.maximize_window()

    def test_upload_dataset(self):
        driver = self.driver

        # Accede a la página de carga (esto depende de tu estructura de frontend)
        driver.get("http://127.0.0.1:5000/fakenodo/upload")
        
        # Localiza el formulario de carga de archivo
        file_input = driver.find_element(By.NAME, "file")
        
        # Elige un archivo para subir (ajusta la ruta del archivo)
        file_input.send_keys("/path/to/test_dataset.txt")

        # Envía el formulario
        submit_button = driver.find_element(By.XPATH, "//button[text()='Upload']")  # Asegúrate de que el botón sea correcto
        submit_button.click()

        # Espera a que el mensaje de éxito o error sea visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "upload_success_message"))  # Ajusta el ID según el HTML
        )
        
        # Verifica que se haya subido correctamente
        success_message = driver.find_element(By.ID, "upload_success_message")
        self.assertIn("Dataset uploaded successfully", success_message.text)

    def test_download_dataset(self):
        driver = self.driver

        # Suponiendo que hemos subido el dataset y tenemos el ID del mismo
        dataset_id = 1

        # Accede a la URL para descargar el dataset
        driver.get(f"http://127.0.0.1:5000/fakenodo/download/{dataset_id}")

        # Espera a que el archivo se haya descargado (esto depende de la implementación del frontend)
        time.sleep(2)  # Ajusta este tiempo según sea necesario para que el archivo se descargue

        # Verifica que el archivo existe en el sistema (asumiendo que se descarga correctamente)
        # Verifica si el archivo fue descargado
        downloaded_file_path = f"/path/to/download/folder/dataset_{dataset_id}.txt"  # Ajusta el path de descarga
        self.assertTrue(os.path.exists(downloaded_file_path))

    def test_delete_dataset(self):
        driver = self.driver

        # Suponiendo que hemos subido un dataset y sabemos el ID
        dataset_id = 1

        # Accede a la URL para eliminar el dataset
        driver.get(f"http://127.0.0.1:5000/fakenodo/dataset/{dataset_id}")

        # Espera y verifica que el dataset haya sido eliminado
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "delete_success_message"))
        )

        # Verifica el mensaje de eliminación
        success_message = driver.find_element(By.ID, "delete_success_message")
        self.assertIn("Dataset deleted successfully", success_message.text)

    @classmethod
    def tearDownClass(cls):
        # Cierra el navegador después de las pruebas
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
