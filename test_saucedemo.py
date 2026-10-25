import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from helpers import BASE_URL, PASSWORD, login, wait_for

BACKPACK_ADD = '[data-test="add-to-cart-sauce-labs-backpack"]'
BACKPACK_REMOVE = '[data-test="remove-sauce-labs-backpack"]'


# 1. Login valid
def test_login_valid_credentials(driver):
    login(driver, "standard_user", PASSWORD)
    wait = wait_for(driver)
    wait.until(EC.url_contains("inventory.html"))
    title = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title")))
    assert title.text == "Products"


# 2-5. Login tidak valid (equivalence partitioning: salah, terkunci, kosong)
@pytest.mark.parametrize(
    "username, password, expected",
    [
        ("standard_user", "password_salah", "do not match"),
        ("locked_out_user", PASSWORD, "locked out"),
        ("", PASSWORD, "Username is required"),
        ("standard_user", "", "Password is required"),
    ],
    ids=["password_salah", "user_terkunci", "username_kosong", "password_kosong"],
)
def test_login_invalid(driver, username, password, expected):
    login(driver, username, password)
    error = wait_for(driver).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="error"]'))
    )
    assert expected in error.text


# 6. Halaman Products
def test_products_page_shows_six_items(logged_in_driver):
    items = logged_in_driver.find_elements(By.CLASS_NAME, "inventory_item")
    assert len(items) == 6


# 7. Sort harga rendah ke tinggi
def test_sort_price_low_to_high(logged_in_driver):
    d = logged_in_driver
    Select(
        d.find_element(By.CSS_SELECTOR, '[data-test="product-sort-container"]')
    ).select_by_value("lohi")
    prices = [
        float(e.text.replace("$", ""))
        for e in d.find_elements(By.CLASS_NAME, "inventory_item_price")
    ]
    assert prices == sorted(prices)


# 8. Tambah produk ke keranjang
def test_add_item_updates_cart_badge(logged_in_driver):
    d = logged_in_driver
    d.find_element(By.CSS_SELECTOR, BACKPACK_ADD).click()
    badge = wait_for(d).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
    )
    assert badge.text == "1"


# 9. Hapus produk dari keranjang
def test_remove_item_hides_cart_badge(logged_in_driver):
    d = logged_in_driver
    d.find_element(By.CSS_SELECTOR, BACKPACK_ADD).click()
    d.find_element(By.CSS_SELECTOR, BACKPACK_REMOVE).click()
    assert wait_for(d).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
    )


# 10. Checkout dari awal sampai selesai
def test_checkout_end_to_end(logged_in_driver):
    d = logged_in_driver
    wait = wait_for(d)
    d.find_element(By.CSS_SELECTOR, BACKPACK_ADD).click()
    d.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="checkout"]'))
    ).click()
    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="firstName"]'))
    ).send_keys("Budi")
    d.find_element(By.CSS_SELECTOR, '[data-test="lastName"]').send_keys("Tester")
    d.find_element(By.CSS_SELECTOR, '[data-test="postalCode"]').send_keys("90111")
    d.find_element(By.CSS_SELECTOR, '[data-test="continue"]').click()
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="finish"]'))
    ).click()
    header = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="complete-header"]'))
    )
    assert header.text == "Thank you for your order!"


# 11. Logout
def test_logout_returns_to_login_page(logged_in_driver):
    d = logged_in_driver
    wait = wait_for(d)
    d.find_element(By.ID, "react-burger-menu-btn").click()
    wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))).click()
    wait.until(EC.visibility_of_element_located((By.ID, "login-button")))
    assert d.current_url == BASE_URL