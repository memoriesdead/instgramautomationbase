"""
Debug script to inspect Instagram signup page structure
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from time import sleep
import os

def get_driver():
    """Get Chrome driver"""
    chrome_options = webdriver.ChromeOptions()
    driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
    if os.path.exists(driver_path):
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    return driver

print("Starting Chrome...")
driver = get_driver()

print("Opening Instagram signup page...")
driver.get("https://www.instagram.com/accounts/emailsignup/")

print("Waiting 5 seconds for page to load...")
sleep(5)

# Save page source
print("\nSaving page source to debug_page.html...")
with open("debug_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("\nLooking for input fields...")
try:
    # Try to find all input fields
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"Found {len(inputs)} input fields:")
    for i, inp in enumerate(inputs):
        name = inp.get_attribute("name")
        placeholder = inp.get_attribute("placeholder")
        input_type = inp.get_attribute("type")
        print(f"  {i+1}. Type: {input_type}, Name: {name}, Placeholder: {placeholder}")
except Exception as e:
    print(f"Error finding inputs: {e}")

print("\nLooking for buttons...")
try:
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"Found {len(buttons)} buttons:")
    for i, btn in enumerate(buttons):
        text = btn.text
        btn_type = btn.get_attribute("type")
        print(f"  {i+1}. Type: {btn_type}, Text: '{text}'")
except Exception as e:
    print(f"Error finding buttons: {e}")

print("\nTaking screenshot...")
driver.save_screenshot("instagram_signup_page.png")
print("Screenshot saved as instagram_signup_page.png")

print("\n" + "="*60)
print("Debug complete! Check the following files:")
print("  - debug_page.html (page source)")
print("  - instagram_signup_page.png (screenshot)")
print("="*60)

input("\nPress Enter to close the browser...")
driver.quit()
