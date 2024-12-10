from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.selenium.common import initialize_driver


class TestDatasetRateSelenium:
    def setup_method(self):
        self.driver = initialize_driver()
        self.driver.implicitly_wait(10)

    def teardown_method(self):
        self.driver.quit()

    def login(self, email, password):
        """Helper method for logging in."""
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "submit").click()

    def rate_dataset(self, dataset_name, rating_value):
        """Helper method for rating a dataset."""
        self.driver.find_element(By.LINK_TEXT, dataset_name).click()

        dropdown = self.driver.find_element(By.ID, "rating-select")
        dropdown.find_element(By.XPATH, f"//option[. = '{rating_value}']").click()

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(3)").click()

        WebDriverWait(self.driver, 10).until(
            EC.alert_is_present()
        )
        alert = self.driver.switch_to.alert
        assert alert.text == "Rating sent successfully"
        alert.accept()

    def test_rate_valid_dataset(self):
        """Test rating a valid dataset."""
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(945, 1016)

        self.login("user1@example.com", "1234")
        self.rate_dataset("Sample dataset 4", "4")

    def test_rate_invalid_dataset(self):
        """Test rating an invalid dataset (nonexistent)."""
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(945, 1016)

        self.login("user1@example.com", "1234")

        self.driver.get("http://localhost:5000/dataset/nonexistent")
        error_message = self.driver.find_element(By.CLASS_NAME, "error-message").text

        assert error_message == "Dataset not found"

    def test_change_rating(self):
        """Test changing the rating of a dataset."""
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(945, 1016)

        self.login("user1@example.com", "1234")
        self.rate_dataset("Sample dataset 4", "3")  
        self.rate_dataset("Sample dataset 4", "5")  

        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        selected_option = self.driver.find_element(By.ID, "rating-select").get_attribute("value")
        assert selected_option == "5"

    def test_rate_without_login(self):
        """Test rating a dataset without logging in."""
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(945, 1016)

        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        error_message = self.driver.find_element(By.CLASS_NAME, "error-message").text

        assert error_message == "You must be logged in to rate a dataset"
