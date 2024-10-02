from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Đường dẫn đến WebDriver (ví dụ: Chrome)
driver = webdriver.Chrome(executable_path='/path/to/chromedriver')

# Mở trang đổi mật khẩu Netflix
driver.get("https://www.netflix.com/password")

# Đợi trang tải
time.sleep(3)

# Tìm các trường nhập liệu dựa trên class hoặc data-uia
current_password_field = driver.find_element(By.CSS_SELECTOR, 'li[data-uia="field-currentPassword+wrapper"] input')
new_password_field = driver.find_element(By.CSS_SELECTOR, 'li[data-uia="field-newPassword+wrapper"] input')
confirm_password_field = driver.find_element(By.CSS_SELECTOR, 'li[data-uia="field-confirmNewPassword+wrapper"] input')

# Điền mật khẩu cũ và mới
current_password_field.send_keys("matkhaucu")
new_password_field.send_keys("matkhaumoi")
confirm_password_field.send_keys("matkhaumoi")

# Click nút lưu thay đổi
save_button = driver.find_element(By.CSS_SELECTOR, 'div.nf-btn-bar.change-password-buttons button[type="submit"]')
save_button.click()

# Đợi một chút để chắc chắn thông tin được gửi
time.sleep(5)

# Đóng trình duyệt
driver.quit()
