import re
import time
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
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
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--headless=new")
options.add_argument("--log-level=3")

driver = webdriver.Edge(options=options)
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
def scrape_data():
    url = "https://www.pickles.com.au/used/search/lob/salvage?search=m2%2Cm3%2Cm4&page=1&limit=120"
    try:
        driver.get(url)
        listings = []
        for i in range(1, 3):
            try:
                print(f"⏳ Processing element {i}...")
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
                    "Model": driver.find_element(By.XPATH, "//h1").text[5:] if driver.find_element(By.XPATH, "//h1").text else "N/A",
                    "Year": driver.find_element(By.XPATH, "//h1").text[0:4] if driver.find_element(By.XPATH, "//h1").text else "N/A",
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
                save_data(data)
                driver.back()
                time.sleep(3)
                return listings.append(data)
            except:
                continue
    finally:
        driver.quit()
scrape_data()
