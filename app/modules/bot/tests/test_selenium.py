from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def test_bot_list():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        try:
            # Set window to correct size
            driver.set_window_size(992, 1108)
            # Open home page
            driver.get("http://localhost/")
            # Go to login page
            driver.find_element(By.LINK_TEXT, "Login").click()
            # Click on email text field
            driver.find_element(By.ID, "email").click()
            # Write email
            driver.find_element(By.ID, "email").send_keys("user1@example.com")
            # Click on password field
            driver.find_element(By.ID, "password").click()
            # Enter password
            driver.find_element(By.ID, "password").send_keys("1234")
            # Click on remember me
            driver.find_element(By.ID, "remember_me").click()
            # Click on login button
            driver.find_element(By.ID, "submit").click()
            # Open sidebar
            driver.find_element(By.CSS_SELECTOR, ".hamburger").click()
            # Go to My Bots page
            driver.find_element(By.LINK_TEXT, "My bots").click()
            # Check the sample bot is present
            assert driver.find_element(By.CSS_SELECTOR, "td > strong").text == "Bot 1"
            # Check the sample bot is enabled
            assert driver.find_element(By.CSS_SELECTOR, ".badge").text == "Enabled"
            # Open profile dropdown
            driver.find_element(By.LINK_TEXT, "Doe, John").click()
            # Click on log out button
            driver.find_element(By.LINK_TEXT, "Log out").click()

            print('List bots test passed!')

        except NoSuchElementException as e:
            print('List bots test failed!')
            print(e)

    finally:

        # Close the browser
        close_driver(driver)


def test_bot_create_and_delete():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        try:
            # Set window to correct size
            driver.set_window_size(992, 1108)
            # Open home page
            driver.get("http://localhost/")
            # Go to login page
            driver.find_element(By.LINK_TEXT, "Login").click()
            # Click on email text field
            driver.find_element(By.ID, "email").click()
            # Write email
            driver.find_element(By.ID, "email").send_keys("user1@example.com")
            # Click on password field
            driver.find_element(By.ID, "password").click()
            # Enter password
            driver.find_element(By.ID, "password").send_keys("1234")
            # Click on remember me
            driver.find_element(By.ID, "remember_me").click()
            # Click on login button
            driver.find_element(By.ID, "submit").click()
            # Open sidebar
            driver.find_element(By.CSS_SELECTOR, ".hamburger").click()
            # Go to My Bots page
            driver.find_element(By.LINK_TEXT, "My bots").click()
            # Check the sample bot is present
            assert driver.find_element(By.CSS_SELECTOR, "td > strong").text == "Bot 1"
            # Check the sample bot is enabled
            assert driver.find_element(By.CSS_SELECTOR, ".badge").text == "Enabled"
            # Click Create bot button
            driver.find_element(By.LINK_TEXT, "Create bot").click()
            # Click in name text field
            driver.find_element(By.ID, "name").click()
            # Enter name
            driver.find_element(By.ID, "name").send_keys("Bot 2")
            # Select JSON service (the only one that can act as dummy)
            dropdown = driver.find_element(By.ID, "service_name")
            dropdown.find_element(By.XPATH, "//option[. = 'Discord']").click()
            # Click on service URL text field
            driver.find_element(By.ID, "service_url").click()
            # Enter dummy URL
            driver.find_element(By.ID, "service_url").send_keys("test://test/test")
            # Activate "On download dataset"
            driver.find_element(By.ID, "on_download_dataset").click()
            # Activate "On download file"
            driver.find_element(By.ID, "on_download_file").click()
            # Click on Test button
            driver.find_element(By.ID, "test-button").click()
            # Check if submit button is enabled
            assert driver.find_element(By.ID, "save-button").is_enabled()
            # Click on Save button
            driver.find_element(By.ID, "save-button").click()
            # Check the created bot is in the list
            assert driver.find_element(By.XPATH, "//strong[contains(.,\'Bot 2\')]").text == "Bot 2"
            # Check the new bot is enabled
            assert driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .bg-success").text == "Enabled"
            driver.find_element(By.CSS_SELECTOR, "tr:nth-child(2) .d-inline .text-danger").send_keys(Keys.ENTER)
            assert driver.switch_to.alert.text == "Are you sure you wish to delete?"
            driver.switch_to.alert.accept()
            driver.refresh()
            # Open profile dropdown
            driver.find_element(By.LINK_TEXT, "Doe, John").click()
            # Click on log out button
            driver.find_element(By.LINK_TEXT, "Log out").click()

            print('List bots create and delete passed!')

        except NoSuchElementException as e:
            print('List bots test failed!')
            print(e)

    finally:

        # Close the browser
        close_driver(driver)


def test_bot_edit():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        try:
            # Set window to correct size
            driver.set_window_size(992, 1108)
            # Open home page
            driver.get("http://localhost/")
            # Go to login page
            driver.find_element(By.LINK_TEXT, "Login").click()
            # Click on email text field
            driver.find_element(By.ID, "email").click()
            # Write email
            driver.find_element(By.ID, "email").send_keys("user1@example.com")
            # Click on password field
            driver.find_element(By.ID, "password").click()
            # Enter password
            driver.find_element(By.ID, "password").send_keys("1234")
            # Click on remember me
            driver.find_element(By.ID, "remember_me").click()
            # Click on login button
            driver.find_element(By.ID, "submit").click()
            # Open sidebar
            driver.find_element(By.CSS_SELECTOR, ".hamburger").click()
            # Go to My Bots page
            driver.find_element(By.LINK_TEXT, "My bots").click()
            # Check the sample bot is present
            assert driver.find_element(By.CSS_SELECTOR, "td > strong").text == "Bot 1"
            # Check the sample bot is enabled
            assert driver.find_element(By.CSS_SELECTOR, ".badge").text == "Enabled"
            # Click on edit icon
            driver.find_element(By.CSS_SELECTOR, ".feather-edit").click()
            # Change bot name
            driver.find_element(By.ID, "name").clear()
            driver.find_element(By.ID, "name").send_keys("Bot 2")
            # Click on test button
            driver.find_element(By.ID, "test-button").click()
            # Click on save button
            driver.find_element(By.ID, "save-button").click()
            # Check success message is present
            assert driver.find_element(By.CSS_SELECTOR, "p:nth-child(2)").text == "Bot edited successfully"
            # Check bot name was changed
            assert driver.find_element(By.CSS_SELECTOR, "td > strong").text == "Bot 2"
            # Click on edit icon
            driver.find_element(By.CSS_SELECTOR, ".feather-edit").click()
            # Change bot name back
            driver.find_element(By.ID, "name").clear()
            driver.find_element(By.ID, "name").send_keys("Bot 1")
            # Click on test button
            driver.find_element(By.ID, "test-button").click()
            # Click on save button
            driver.find_element(By.ID, "save-button").click()
            # Check success message is present
            assert driver.find_element(By.CSS_SELECTOR, "p:nth-child(2)").text == "Bot edited successfully"
            # Check bot name was changed
            assert driver.find_element(By.CSS_SELECTOR, "td > strong").text == "Bot 1"
            # Open profile dropdown
            driver.find_element(By.LINK_TEXT, "Doe, John").click()
            # Click on log out button
            driver.find_element(By.LINK_TEXT, "Log out").click()

            print('List bots edit passed!')

        except NoSuchElementException as e:
            print('List bots test failed!')
            print(e)

    finally:

        # Close the browser
        close_driver(driver)



# Call the test function
test_bot_list()
test_bot_create_and_delete()
test_bot_edit()
