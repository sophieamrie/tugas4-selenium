from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.saucedemo.com/"
PASSWORD = "secret_sauce"


def wait_for(driver, timeout=10):
    return WebDriverWait(driver, timeout)


def login(driver, username, password):
    driver.get(BASE_URL)
    wait_for(driver).until(
        EC.visibility_of_element_located((By.ID, "user-name"))
    ).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()