from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import re
import time

def has_consecutive_digits(phone_number):
    # Remove all non-numeric characters
    digits = re.sub(r'\D', '', phone_number)

    # Count unique digits in the phone number
    unique_digits = set(digits)
    if len(unique_digits) <= 3:
        return True, f"Limited unique digits: {len(unique_digits)} ({', '.join(unique_digits)})"
    
    # Find all triplets (3 consecutive same digits)
    triplets = []
    for i in range(len(digits) - 2):
        if digits[i] == digits[i+1] == digits[i+2]:
            triplets.append(digits[i:i+3])
    
    # Find all doubles (2 consecutive same digits)
    doubles = []
    i = 0
    while i < len(digits) - 1:
        if digits[i] == digits[i+1]:
            doubles.append(digits[i:i+2])
            i += 2  # Skip both digits of the pair
        else:
            i += 1
    
    # Check for 2 triplets and 1 double
    if len(triplets) >= 2 and len(doubles) >= 1:
        return True, f"Two triplets and one double: triplets={triplets}, doubles={doubles}"
    
    # Check for 4 doubles
    if len(doubles) >= 4:
        return True, f"Four doubles: {doubles}"
    
    return False, None

def check_free_mobile_numbers():
    # Firefox configuration
    options = Options()
    # Uncomment the line below to run in headless mode
    # options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    try:
        while True:
            # Access the page
            driver.get("https://mobile.free.fr/souscription/options")

            # Wait for page to load - using a more reliable element
            # try:
            #     WebDriverWait(driver, 1).until(
            #         EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Configuration de ma ligne')]"))
            #     )
            # except:
            #     print("Waiting for page to load...")
            #     time.sleep(3)

            # Delete all cookies
            driver.delete_all_cookies()

            # Refresh the page
            driver.refresh()

            # Wait for page to reload
            # try:
            #     WebDriverWait(driver, 1).until(
            #         EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Configuration de ma ligne')]"))
            #     )
            # except:
            #     print("Waiting for page to reload...")
            #     time.sleep(3)

            # Click on "Je choisis un nouveau numéro" radio button
            try:
                # Based on the attached image, we can see the radio button is already selected
                # But we'll click it to ensure it's selected
                new_number_radio = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='radio']/following-sibling::div[contains(text(), 'Je choisis un nouveau numéro')]"))
                )
                driver.execute_script("arguments[0].click();", new_number_radio)
                print("Selected 'Je choisis un nouveau numéro'")
            except:
                try:
                    # Alternative approach
                    new_number_radio = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[text()='Je choisis un nouveau numéro']"))
                    )
                    driver.execute_script("arguments[0].click();", new_number_radio)
                    print("Selected 'Je choisis un nouveau numéro' (alternative method)")
                except:
                    print("Could not select 'Je choisis un nouveau numéro'. It might already be selected.")

            # Wait for the dropdown field to appear and click it
            try:
                # From the image, we can see the dropdown field
                dropdown = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dropdown') or contains(@role, 'listbox')]"))
                )
                dropdown.click()
                print("Clicked on dropdown")
            except:
                try:
                    # Try clicking the dropdown by the arrow icon label
                    arrow_icon = driver.find_element(By.XPATH, "//i[contains(@class, 'icon-arrow-down-s-line')]")
                    driver.execute_script("arguments[0].click();", arrow_icon)
                    print("Clicked on dropdown arrow field")
                except:
                    print("Could not click on dropdown. Trying JavaScript click...")
                    try:
                        # Find the dropdown input element
                        dropdown_input = driver.find_element(By.ID, "8310")
                        # Use JavaScript to click on it
                        driver.execute_script("arguments[0].click();", dropdown_input)
                    except:
                        print("Failed to open dropdown. Retrying...")
                        continue

            # Wait for options to appear
            time.sleep(1)

            # Get all available phone numbers from the dropdown
            try:
                # Wait for the dropdown list to appear
                WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'absolute') and contains(@class, 'rounded-8')]"))
                )

                # Find all li elements inside the dropdown ul
                number_options = driver.find_elements(By.XPATH, "//ul[contains(@class, 'absolute') and contains(@class, 'rounded-8')]/li")
                print(f"Found {len(number_options)} phone numbers")

                if not number_options:
                    # Try alternative selector - directly find elements that look like phone numbers
                    number_options = driver.find_elements(By.XPATH, "//li[contains(text(), '07') or contains(text(), '06')]")
                    print(f"Found {len(number_options)} phone numbers with alternative selector")

                    # If still no results, try another approach based on the image
                    if not number_options:
                        number_options = driver.find_elements(By.XPATH, "//ul[contains(@class, 'absolute')]//*[contains(text(), '07') or contains(text(), '06')]")
                        print(f"Found {len(number_options)} phone numbers with second alternative selector")
            except Exception as e:
                print(f"Could not find phone number options. Error: {e}. Retrying...")
                continue

            found_consecutive = False

            # Check each number for consecutive digits
            for option in number_options:
                phone_number = option.text.strip()
                if not phone_number:
                    continue

                print(f"Checking number: {phone_number}")
                has_consecutive, sequence = has_consecutive_digits(phone_number)

                if has_consecutive:
                    print(f"Found number with consecutive digits: {phone_number}")
                    print(f"Consecutive sequence: {sequence}")
                    found_consecutive = True

                    # Try to select this number
                    try:
                        driver.execute_script("arguments[0].click();", option)
                        print("Successfully selected the number.")
                    except Exception as e:
                        print(f"Could not click on the number option. Error: {e}")
                        try:
                            option.click()
                            print("Successfully selected the number with direct click.")
                        except:
                            print("Both click methods failed.")

                    # Pause for user to decide
                    user_input = input("Press Enter to continue searching or type 'stop' to keep this number: ")
                    if user_input.lower() == 'stop':
                        print(f"Selected number: {phone_number}")
                        return
                    else:
                        break  # Break the loop to refresh and get new numbers

            if not found_consecutive:
                print("No numbers with consecutive digits found in this batch. Trying again...")

            time.sleep(1)


    except KeyboardInterrupt:
        print("Search stopped by user.")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_free_mobile_numbers()
