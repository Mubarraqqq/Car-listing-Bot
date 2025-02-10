import re
import time
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests


# Database Connection
def connect_db():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",  # Update user
            password="your_password",  # Update password
            database="car_listings",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f"❌ Database connection error: {e}")
        return None

# Selenium WebDriver Configuration
options = Options()
options.binary_location = "/usr/bin/chromium"  # Ensure Selenium finds Chromium
options.add_argument("--headless")  # Run without UI
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Use the system-installed ChromeDriver
service = Service("/usr/bin/chromedriver")

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 50)

# Function to Save Data into the Database and Web Interface
def save_data(data):
    try:
        db = connect_db()
        if db:
            with db.cursor() as cursor:
                sql = """
                INSERT INTO listings (
                VIN, Registration, Model, Year, Engine_Capacity, Transmission, Drive_Type, Fuel, Cylinders, No_of_Doors, Color, WOVR_Status, Incident_Type, Compliance_Date, GST_Status,
                Bidding_Time, Location, Views, Watchers, Image_URL
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE bidding_time = VALUES(bidding_time)
                """
                values = (
                    data.get("VIN", "N/A"),
                    data.get("Registration", "N/A"),
                    data.get("Model", "N/A"),
                    data.get("Year", "N/A"),
                    data.get("Engine_Capacity", "N/A"),
                    data.get("Transmission", "N/A"),
                    data.get("Drive_Type", "N/A"),
                    data.get("Fuel", "N/A"),
                    data.get("Cylinders", "N/A"),
                    data.get("No_of_Doors", "N/A"),
                    data.get("Color", "N/A"),
                    data.get("WOVR_Status", "N/A"),
                    data.get("Incident_Type", "N/A"),
                    data.get("Compliance_Date", "N/A"),
                    data.get("GST_Status", "N/A"),
                    data.get("Bidding_Time", "N/A"),
                    data.get("Location", "N/A"),
                    data.get("Views", "0"),
                    data.get("Watchers", "0"),
                    data.get("Image_URL", "N/A")
                )
                cursor.execute(sql, values)
                db.commit()
                print(f"✅ Data inserted for {data.get('VIN', 'Unknown')}")
    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if db:
            db.close()

    # Send data to web interface
    try:
        requests.post("http://localhost:5000/update", json=data)
        print("✅ Data sent to web interface")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Web interface update failed: {e}")

# Function to Scrape Data
import pandas as pd  # Import Pandas

def scrape_data():
    print("🚀 scrape_data() has started running!")
    url = "https://www.pickles.com.au/used/search/lob/salvage?search=m2%2Cm3%2Cm4&page=1&limit=120"
    listings = []

    try:
        driver.get(url)
        for i in range(1, 10):
            try:
                print(f"⏳ Processing element {i}...")

                # Check if element is found
                element_xpath = f"/html/body/div[1]/main/section/div/div/section/div/div[{i}]/main/a/section/section[2]/div/pds-button-standard/div/button/p"
                element = wait.until(EC.element_to_be_clickable((By.XPATH, element_xpath)))
                element.click()
                time.sleep(5)

                def safe_get_text(by, selector):
                    try:
                        return driver.find_element(by, selector).text
                    except:
                        return "N/A"

                image = driver.find_element(By.CSS_SELECTOR, 'button.styles_embla-thumbs__slide__number__4FZmu').get_attribute("style")
                image_url = re.search(r'url\((.*?)\)', image).group(1)

                data = {
                    "VIN": safe_get_text(By.ID, "vin-desktop-only"),
                    "Registration": safe_get_text(By.ID, "registration-desktop-only"),
                    "Model": safe_get_text(By.XPATH, "//h1"),
                    "Year": safe_get_text(By.XPATH, "//h1")[:4] if safe_get_text(By.XPATH, "//h1") else "N/A",
                    "Engine_Capacity": safe_get_text(By.ID, "engineCapacity-desktop-only"),
                    "Transmission": safe_get_text(By.ID, "transmission-desktop-only"),
                    "Drive_Type": safe_get_text(By.ID, "driveType-desktop-only"),
                    "Fuel": safe_get_text(By.ID, "fuel-desktop-only"),
                    "Cylinders": safe_get_text(By.ID, "numberOfCylinders-desktop-only"),
                    "No_of_Doors": safe_get_text(By.ID, "noOfDoors-desktop-only"),
                    "Color": safe_get_text(By.XPATH, "(//span[@class='styles_label__78OYp'])[1]"),
                    "Bidding_Time": safe_get_text(By.XPATH, "(//span[@class='styles_text__kdj5N'])"),
                    "Location": safe_get_text(By.XPATH, '//*[@id="pd-pl-product-location"]/span[2]'),
                    "Views": safe_get_text(By.XPATH, "(//span[@class='styles_value__p1VVf'])[1]"),
                    "Watchers": safe_get_text(By.XPATH, "(//span[@class='styles_value__p1VVf'])[2]"),
                    "Image_URL": image_url,
                }

                print(f"✅ Scraped Data: {data}")  # Debugging print

                listings.append(data)
                driver.back()
                time.sleep(3)

            except Exception as e:
                print(f"⚠️ Skipping element {i} due to error: {e}")
                continue
    finally:
        driver.quit()

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(listings)

    print(f"📢 Final Scraped Data (as DataFrame):\n{df}")  # Debugging print
    return df  # Return the DataFrame


if __name__=='__main__':
    scrape_data()
