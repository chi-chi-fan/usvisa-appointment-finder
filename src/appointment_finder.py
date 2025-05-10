import datetime
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from creds import username, password, facility_names, latest_notification_date, seconds_between_checks
from telegram import send_message, send_photo
from urls import BASE_URL, SIGN_IN_URL, SCHEDULE_URL, APPOINTMENTS_URL


def log_in(driver):
    print('Logging in.')
    print(f"Using credentials: {username=} {password=}")
    print(f"Current URL: {driver.current_url}")

    # Wait for email field to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'user[email]'))
    )

    # Fill in email
    user_box = driver.find_element(By.NAME, 'user[email]')
    user_box.clear()
    user_box.send_keys(username)

    # Fill in password
    password_box = driver.find_element(By.NAME, 'user[password]')
    password_box.clear()
    password_box.send_keys(password)

    # Click the checkbox using JavaScript to bypass style overlays
    checkbox = driver.find_element(By.ID, 'policy_confirmed')
    driver.execute_script("arguments[0].click();", checkbox)

    # Click the sign-in button
    sign_in_button = driver.find_element(By.NAME, 'commit')
    sign_in_button.click()

    # Wait for the login to process
    time.sleep(3)

    # Save screenshot for debugging
    driver.save_screenshot("post_login.png")

    if "sign_in" in driver.current_url:
        print("❌ Login failed. Still on sign-in page.")
    else:
        print("✅ Login successful.")


def is_worth_notifying(year, month, days):
    first_available_date_object = datetime.datetime.strptime(
        f'{year}-{month}-{days[0]}', "%Y-%B-%d")
    latest_notification_date_object = datetime.datetime.strptime(
        latest_notification_date, '%Y-%m-%d')
    return first_available_date_object <= latest_notification_date_object


def check_appointments(driver):
    driver.get(SIGN_IN_URL)  # ✅ Start at the correct login page
    log_in(driver)

    if "sign_in" in driver.current_url:
        print("Login failed — still on sign-in page.")
        driver.save_screenshot("login_failed.png")
        return

    driver.get(APPOINTMENTS_URL)

    # Click "Continue" if visible
    try:
        continue_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'primary'))
        )
        if continue_button.get_property('value') == 'Continue':
            continue_button.click()
            print("Clicked continue button.")
    except:
        print("No 'Continue' button found — possibly not needed.")

    try:
        facility_select = Select(driver.find_element(
          By.ID, 'appointments_consulate_appointment_facility_id'))

        for city in facility_names:
            print(f"🔍 Checking appointments for {city}...")
            facility_select.select_by_visible_text(city)
            time.sleep(1)

            if driver.find_element(By.ID, 'consulate_date_time_not_available').is_displayed():
                print(f"No dates available for {city}")
                continue

            # Open the calendar
            driver.find_element(
                By.ID, 'appointments_consulate_appointment_date').click()

            for date_picker in driver.find_elements(By.CLASS_NAME, 'ui-datepicker-group'):
                day_elements = date_picker.find_elements(By.TAG_NAME, 'td')
                available_days = [day_element.find_element(By.TAG_NAME, 'a').get_attribute("textContent")
                                for day_element in day_elements if day_element.get_attribute("class") == ' undefined']
                if available_days:
                    month = date_picker.find_element(
                        By.CLASS_NAME, 'ui-datepicker-month').get_attribute("textContent")
                    year = date_picker.find_element(
                        By.CLASS_NAME, 'ui-datepicker-year').get_attribute("textContent")
                    message = f'📅 Available days in {city} - {month} {year}: {", ".join(available_days)}\nLink: {SIGN_IN_URL}'
                    print(message)

                    if not is_worth_notifying(year, month, available_days):
                        print("Not worth notifying.")
                        continue

                    send_message(message)
                    send_photo(driver.get_screenshot_as_png())
                    return  # exit after first hit

        # Check for system busy message
        if "System is busy" in driver.page_source:
            print("⚠️ System busy. Will try again later.")
            driver.save_screenshot("system_busy.png")
            return

    except Exception as e:
        print(f"⚠️ Error selecting facility: {e}")
        driver.save_screenshot("facility_selection_failed.png")
        return

    # Check if no dates are available
    if driver.find_element(By.ID, 'consulate_date_time_not_available').is_displayed():
        print("No dates available")
        return

    # Click on the calendar to load dates
    driver.find_element(By.ID, 'appointments_consulate_appointment_date').click()

    while True:
        for date_picker in driver.find_elements(By.CLASS_NAME, 'ui-datepicker-group'):
            day_elements = date_picker.find_elements(By.TAG_NAME, 'td')
            available_days = [day_element.find_element(By.TAG_NAME, 'a').get_attribute("textContent")
                              for day_element in day_elements if day_element.get_attribute("class") == ' undefined']
            if available_days:
                month = date_picker.find_element(By.CLASS_NAME, 'ui-datepicker-month').get_attribute("textContent")
                year = date_picker.find_element(By.CLASS_NAME, 'ui-datepicker-year').get_attribute("textContent")
                message = f'Available days found in {month} {year}: {", ".join(available_days)}. Link: {SIGN_IN_URL}'
                print(message)

                if not is_worth_notifying(year, month, available_days):
                    print("Not worth notifying.")
                    return

                send_message(message)
                send_photo(driver.get_screenshot_as_png())
                return

        # Advance calendar view
        driver.find_element(By.CLASS_NAME, 'ui-datepicker-next').click()
        driver.find_element(By.CLASS_NAME, 'ui-datepicker-next').click()


def main():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    while True:
        current_time = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        print(f'Starting a new check at {current_time}.')
        try:
            check_appointments(driver)
        except Exception as err:
            print(f'Exception: {err}')
        time.sleep(seconds_between_checks)


if __name__ == "__main__":
    main()