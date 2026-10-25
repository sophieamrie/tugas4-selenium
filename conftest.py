import os

import pytest
import pytest_html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helpers import PASSWORD, login, wait_for


def pytest_html_report_title(report):
    report.title = "Laporan Tugas 4 - Selenium WebDriver (SauceDemo)"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,900")
    # HEADLESS=1 dipakai nanti saat CI/CD (tanpa jendela browser)
    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )

    # SELENIUM_REMOTE_URL dipakai nanti untuk Selenium Grid
    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    if remote_url:
        drv = webdriver.Remote(command_executor=remote_url, options=options)
    else:
        drv = webdriver.Chrome(options=options)

    yield drv
    drv.quit()


@pytest.fixture
def logged_in_driver(driver):
    login(driver, "standard_user", PASSWORD)
    wait_for(driver).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "inventory_item"))
    )
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Kalau tes gagal, ambil screenshot dan tempel ke laporan HTML."""
    outcome = yield
    report = outcome.get_result()
    if report.when in ("setup", "call") and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            extras = getattr(report, "extras", [])
            extras.append(pytest_html.extras.png(drv.get_screenshot_as_base64()))
            report.extras = extras