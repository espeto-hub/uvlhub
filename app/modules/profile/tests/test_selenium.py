# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestCheckdatasetuser():
    def setup_method(self, method):
        self.driver = webdriver.Chrome(service="/usr/bin/chromedriver")
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_checkdatasetuser(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1048)
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        self.driver.find_element(By.LINK_TEXT, "Doe, Jane").click()
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 2").click()