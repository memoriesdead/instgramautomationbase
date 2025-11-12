#imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from time import sleep
from random import randint
from datetime import datetime,timedelta
import csv
import shutil
import sys
import os
import schedule
import functions
import createRandom
import login_bot
import first

# Import email verification module
try:
    from email_verifier import get_instagram_verification_code
    from email_config import EMAIL_CONFIG
    EMAIL_AUTOMATION_AVAILABLE = True
except ImportError:
    EMAIL_AUTOMATION_AVAILABLE = False
    print("Warning: Email automation not configured")


def get_driver():
    """Try to get a working webdriver (Chrome first, then Firefox)"""
    # Try Chrome first with local chromedriver
    try:
        print("Attempting to start Chrome...")
        chrome_options = webdriver.ChromeOptions()

        # Try to use local chromedriver.exe first
        if os.path.exists("chromedriver.exe"):
            print("Using local chromedriver.exe...")
            service = ChromeService(executable_path="chromedriver.exe")
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Fall back to automatic ChromeDriver
            driver = webdriver.Chrome(options=chrome_options)

        print("Chrome started successfully!")
        return driver
    except Exception as chrome_error:
        print(f"Chrome failed: {chrome_error}")

    # Try Firefox as fallback
    try:
        print("Attempting to start Firefox...")
        firefox_options = webdriver.FirefoxOptions()
        # Check if geckodriver.exe exists in current directory
        if os.path.exists("geckodriver.exe"):
            service = FirefoxService(executable_path="geckodriver.exe")
            driver = webdriver.Firefox(service=service, options=firefox_options)
        else:
            driver = webdriver.Firefox(options=firefox_options)
        print("Firefox started successfully!")
        return driver
    except Exception as firefox_error:
        print(f"Firefox failed: {firefox_error}")

    # If both fail
    print("\nERROR: Could not start Chrome or Firefox!")
    print("Please ensure one of the following:")
    print("1. Google Chrome is installed")
    print("2. Mozilla Firefox is installed")
    print("3. ChromeDriver or GeckoDriver is available")
    raise Exception("No browser available")


#We definne the class instabot
class instaBot:
    def __init__(self, account_data=None):

        #We ask the user if he want his password, fullname, email, username, birthday and profile photo to be: auto-generated
        #or if he want to specify the properties  with  inputs
        if account_data is None:
            self.mode=input("Mode (write/w, auto/a, spreadsheet/s):  ")
        else:
            self.mode="spreadsheet"

        #if he want to write it himself 
        if self.mode=="w" or self.mode=="write":
            #it ask for the phone number or email, fullname, username, password and birth date
            self.phone_number=str(input("Phone_number or email:  "))
            self.fullname=str(input("Fullname:  "))
            self.username=str(input("Username:  "))
            self.password=str(input("Password:  "))  
            cumpleaños=input("Birth day: (D/M/Y) ")

            #here we are separating the birth into day, month and year 
            #and converting the year into the neccessary index
            cumpleaños_list=cumpleaños.split("/")
            self.day=cumpleaños_list[0]
            self.month=cumpleaños_list[1]
            year=cumpleaños_list[2]
            año_actual = "2021-04-22 00:00:00"
            ahora = datetime.strptime(año_actual, '%Y-%m-%d %H:%M:%S')
            fecha = str(ahora - timedelta(days=int(year)*365))
            fecha_lista=fecha.split("-")
            index_year=fecha_lista[0]
            self.index_year=index_year.lstrip("0")


        #if the user wants the properties to be auto-generated:
        elif self.mode=="a" or self.mode=="Auto" or self.mode=="Auto-generated":
            #we call the functions of createRandom
            tmp=createRandom.create_random()
            self.phone_number=tmp[0]
            self.fullname=tmp[1]
            self.username=tmp[2]
            self.password=tmp[3]

        #if the user wants to use spreadsheet mode:
        elif self.mode=="s" or self.mode=="spreadsheet":
            if account_data is None:
                print("Error: No account data provided for spreadsheet mode")
                sys.exit(1)
            self.account_data = account_data  # Store for later use (username retries)
            self.phone_number=account_data['email']
            self.fullname=account_data['first_name'] + " " + account_data['last_name']
            self.username=account_data['first_name'] + account_data['last_name'] + str(randint(10,99))
            self.password=account_data['password']

        #If the mode is not correct, we finish the program
        else:
            print("The mode must be write, w, a, auto, auto-generated, s, or spreadsheet")
            sys.exit(1)


        # Profile picture option commented out for automation
        # want=input("Do you want to add a profile picture?  ")
        # if want=="y" or want=="yes":

        #     #we delete the folder
        #     try:
        #         shutil.rmtree(".\\Instagram profile image", ignore_errors=True)
        #         sleep(2)
        #
        #     except:
        #         pass

        #     #We create a folder to store the profile image
        #     try:
        #         path = ".\\Pictures"
        #         path = os.path.join(path, "Instagram profile image")
        #         os.mkdir(path)
        #         sleep(1)

        #     except:
        #         pass


        #     #we ask for the location of the profile picture
        #     location=input("Enter the path of your profile image:  ")

        #     try:
        #         #and we copy and rename the image to the appropiate folder
        #         os.replace(location, ".\\Pictures\\Instagram profile image\\descarga.jpg")

        #     except:
        #         pass

        # else:
        #     pass
        

        #we call the function to store all the data of our bot in a csv
        self.put_data_in_table()

        #we set the driver
        self.driver = get_driver()

        #we call the create_account function
        self.create_account()
        

    #function to create the account
    def create_account(self):
        #we open instagram:
        self.driver.get("https://www.instagram.com/accounts/emailsignup/")
        sleep(3)

        # Try to handle cookie consent banner if it appears
        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept')]"))
            )
            cookie_button.click()
            print("Accepted cookies")
            sleep(1.5)
        except:
            print("No cookie banner found or already accepted")
            pass

        sleep(2)

        #we pass the phone number, fullname, username and password using updated field names
        print("Filling in email/phone...")
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "emailOrPhone"))
        )
        email_input.send_keys(self.phone_number)
        sleep(0.4)

        print("Filling in full name...")
        self.driver.find_element(By.NAME, "fullName").send_keys(self.fullname)
        sleep(0.4)

        # Username retry logic - try up to 5 times if username is taken
        username_accepted = False
        max_username_retries = 5

        for attempt in range(max_username_retries):
            if attempt > 0:
                # Generate new username for retry (only works in spreadsheet mode)
                if hasattr(self, 'account_data'):
                    self.username = self.account_data['first_name'] + self.account_data['last_name'] + str(randint(100,999))
                else:
                    # Fallback: add random numbers to current username
                    self.username = self.username.rstrip('0123456789') + str(randint(100,999))
                print(f"Retry {attempt}: Trying new username: {self.username}")

            print("Filling in username...")
            username_input = self.driver.find_element(By.NAME, "username")
            username_input.clear()
            username_input.send_keys(self.username)
            sleep(0.4)

            print("Filling in password...")
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(self.password)

            sleep(1)
            #we click on Sign up button
            print("Clicking Sign up button...")
            button_clicked = False

            # Method 1: Find submit button with "Sign up" text
            try:
                signup_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                signup_button.click()
                button_clicked = True
                print("✓ Clicked Sign up button (method 1)")
            except:
                pass

            # Method 2: Press Enter on password field
            if not button_clicked:
                try:
                    password_input.send_keys(Keys.RETURN)
                    button_clicked = True
                    print("✓ Submitted via Enter key (method 2)")
                except:
                    pass

            # Method 3: Find any visible button and click it
            if not button_clicked:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if btn.is_displayed() and ("Sign up" in btn.text or "sign up" in btn.text.lower()):
                            btn.click()
                            button_clicked = True
                            print("✓ Clicked button (method 3)")
                            break
                except:
                    pass

            if not button_clicked:
                print("⚠ Warning: Could not click Sign up button")

            sleep(3)

            # Check for username error
            try:
                # Look for error messages near username field
                error_elements = self.driver.find_elements(By.XPATH,
                    "//input[@name='username']/following::*[contains(text(), 'This username') or contains(text(), 'already taken') or contains(text(), \"isn't available\")]"
                )

                if error_elements and any(elem.is_displayed() for elem in error_elements):
                    print(f"⚠ Username '{self.username}' is already taken")
                    # Clear the form for retry
                    continue
                else:
                    # No error found, username accepted
                    print(f"✓ Username '{self.username}' accepted")
                    username_accepted = True
                    break
            except:
                # If we can't find error elements, assume username was accepted
                print(f"✓ Username '{self.username}' accepted (no error detected)")
                username_accepted = True
                break

        if not username_accepted:
            raise Exception(f"Failed to find available username after {max_username_retries} attempts")

        sleep(1)


        #Birthday verification - using fixed date: 5/3/2002 (March 5, 2002)
        print("Waiting for birthday fields...")
        sleep(2)

        try:
            # Find and select month (March = 3)
            print("Selecting birth month (March)...")
            month_select = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//select[@title='Month:' or @aria-label='Month']"))
            )
            Select(month_select).select_by_value("3")
            sleep(0.5)

            # Find and select day (5)
            print("Selecting birth day (5)...")
            day_select = self.driver.find_element(By.XPATH, "//select[@title='Day:' or @aria-label='Day']")
            Select(day_select).select_by_value("5")
            sleep(0.5)

            # Find and select year (2002)
            print("Selecting birth year (2002)...")
            year_select = self.driver.find_element(By.XPATH, "//select[@title='Year:' or @aria-label='Year']")
            Select(year_select).select_by_value("2002")
            sleep(1)

            # Click Next button after birthday selection
            print("Clicking Next button after birthday...")

            # Try multiple methods to click the Next button
            clicked = False

            # Method 1: Find by button text "Next"
            try:
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
                )
                next_button.click()
                clicked = True
                print("✓ Clicked Next button (method 1)")
            except:
                pass

            # Method 2: Find by type=button and visible text
            if not clicked:
                try:
                    next_button = self.driver.find_element(By.XPATH, "//button[@type='button' and contains(., 'Next')]")
                    self.driver.execute_script("arguments[0].click();", next_button)
                    clicked = True
                    print("✓ Clicked Next button (method 2 - JavaScript)")
                except:
                    pass

            # Method 3: Find any button in the form
            if not clicked:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if "Next" in btn.text or "next" in btn.text.lower():
                            self.driver.execute_script("arguments[0].click();", btn)
                            clicked = True
                            print("✓ Clicked Next button (method 3)")
                            break
                except:
                    pass

            if not clicked:
                print("⚠ Warning: Could not click Next button automatically")

            sleep(4)

            # Handle birthday information modal if it appears
            try:
                print("Checking for birthday modal...")
                close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close' or contains(@class, 'Close') or text()='×']"))
                )
                close_button.click()
                print("Closed birthday modal")
                sleep(2)
            except:
                print("No birthday modal found or already closed")
                pass

        except Exception as e:
            print(f"Birthday selection error (might be skipped): {e}")


        #Verification code handling - Automated
        print("\n" + "="*60)
        print(f"VERIFICATION CODE NEEDED for: {self.phone_number}")
        print("="*60)

        # First, click to send verification code via email
        try:
            print("Looking for 'Send via email' or verification code button...")
            sleep(2)

            # Try to find and click email verification button
            email_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(text(), 'email') or contains(text(), 'Email') or contains(text(), 'Send')]"
                ))
            )
            email_button.click()
            print("✓ Clicked to send verification code via email")
            sleep(3)

        except Exception as e:
            print(f"Note: Could not find email button (might already be on email verification): {e}")
            # Continue anyway - might already be on the email verification screen
            pass

        instCode = None

        # Try automated email retrieval first
        if EMAIL_AUTOMATION_AVAILABLE and self.phone_number in EMAIL_CONFIG['credentials']:
            print("Attempting automated code retrieval via IMAP...")
            email_password = EMAIL_CONFIG['credentials'][self.phone_number]

            try:
                instCode = get_instagram_verification_code(
                    email_address=self.phone_number,
                    password=email_password,
                    imap_server=EMAIL_CONFIG['imap_server'],
                    imap_port=EMAIL_CONFIG['imap_port'],
                    use_ssl=EMAIL_CONFIG['use_ssl'],
                    max_wait=EMAIL_CONFIG['max_wait_time']
                )

                if instCode:
                    print(f"✓ Automatically retrieved code: {instCode}")
                else:
                    print("✗ Automated retrieval failed, falling back to manual entry")

            except Exception as e:
                print(f"✗ Email automation error: {e}")
                print("Falling back to manual entry...")

        # Fallback to manual entry if automation fails or not configured
        if not instCode:
            print("\nCheck your email and enter the verification code.")
            print(f"Email: {self.phone_number}")
            print("Webmail: https://170.9.13.229/mail/?_task=mail&_mbox=INBOX")
            print("="*60)
            instCode = input("Enter the 6-digit verification code: ").strip()

        # Enter verification code
        try:
            print("Entering verification code...")
            sleep(2)
            code_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email_confirmation_code"))
            )
            code_input.clear()
            code_input.send_keys(instCode)
            print(f"✓ Entered code: {instCode}")
            sleep(2)

            # Submit the verification code by pressing Enter
            print("Submitting verification code...")
            try:
                code_input.send_keys(Keys.RETURN)
                print("✓ Submitted code via Enter key")
            except Exception as e:
                print(f"Enter key failed, trying button click: {e}")
                # Fallback: Try to click Next button
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if btn.is_displayed() and "Next" in btn.text:
                            btn.click()
                            print("✓ Clicked Next button")
                            break
                except:
                    print("⚠ Could not submit - manual intervention needed")

            sleep(5)

        except Exception as e:
            print(f"Error entering verification code: {e}")
            # Try alternative method
            try:
                print("Trying alternative method...")
                code_input = self.driver.find_element(By.XPATH, "//input[@name='email_confirmation_code' or @type='text']")
                code_input.clear()
                code_input.send_keys(instCode)
                sleep(1)

                # Try to click button
                btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
                self.driver.execute_script("arguments[0].click();", btn)
                sleep(5)
                print("✓ Used alternative method")
            except Exception as e2:
                print(f"Alternative method also failed: {e2}")
                print("⚠ Manual intervention may be required")

        print("\n" + "="*60)
        print("Account creation process completed!")
        print("Please verify the account is working properly.")
        print("="*60)



    def put_data_in_table(self):
        #we  store all the data of our bot in a csv  called bot_properties.csv 
        #(password, username, fullname and phone number)
        with open("bot_properties.csv", "a",newline="") as file:
            writer = csv.writer(file)
            propertie=[[self.phone_number,self.fullname,self.username,self.password]]
            writer.writerows(propertie)

    
    
    def getInstVeriCode(self,mailName,domain,first):
        #function to get the verification code. 
        #It will open the website for fake mails and it will read the code from the mailbox
        #it returns the code
        #it takes as arguments the different parts of the mail
        INST_CODE = 'https://email-fake.com/' + domain + '/' + first
    
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(INST_CODE)
        sleep(13)
        code = self.driver.find_element(By.XPATH, "//*[@id='email-table']/div[2]/div[1]/div/h1").text
        code = code.replace("is your Instagram code", "")
        self.driver.switch_to.window(self.driver.window_handles[0])
        return code



    def get_properties(self):
        #function to return the phone_number and password of our bot
        return self.phone_number, self.password

    def return_driver(self):
        #function to return the driver
        return self.driver


if __name__ == "__main__":
    #We create the bot (creating the object)
    bot1=instaBot()
    #we create an empty list to store the people that we are following
    following=[]
    #we call the function to get the properties of our bot and driver
    properties=bot1.get_properties()
    driver=bot1.return_driver()


    #and then we call the main function in first
    print("entering to first")
    first.main(driver,following)
    print("first finished")
    sleep(3)


    #We set the random hour to execute the script
    random_hour= str(randint(1,23))+":"+str(randint(1,58))


    #All the below will execute the functions code
    #(previously logging in) once a day at the random hour set above
    driver=get_driver()
    schedule.every().day.at(random_hour).do(login_bot.login,properties=properties,driver=driver)


    while True:
        try:
            schedule.run_pending()
            sleep(3)
            functions.Function(driver)
            sleep(5)

        except:
            continue

        sleep(3)

