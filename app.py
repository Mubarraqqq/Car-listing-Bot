import mysql.connector
from flask import Flask, render_template, jsonify, request
import threading
from scrape import scrape_data  # Import your scraping function
import pandas as pd
import os

app = Flask(__name__, template_folder="templates")

# Store scraped data in memory before saving to the database
scraped_data = []

# Enable/Disable database connection for debugging
USE_DATABASE = False  # Set to True when testing DB

# Database connection function
def connect_db():
    if not USE_DATABASE:
        return None  # Bypass database for testing

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="your_username",
            password="your_password",
            database="car_listings"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}", flush=True)
        return None

@app.route("/test")
def test():
    return "✅ Flask is working!", 200  # Quick test route

@app.route("/")
def home():
    """Render the homepage with scraped data."""
    try:
        return render_template("index.html", listings=scraped_data)  # Ensure index.html exists
    except Exception as e:
        print(f"❌ Error loading template: {e}", flush=True)
        return "🔥 Flask is running, but index.html has issues.", 500  # Return a 500 error
@app.route("/fetch_data", methods=["GET"])
def fetch_data():
    """Return the latest scraped data instead of dummy data."""
    print("🔍 Fetch data request received.", flush=True)

    global scraped_data

    # Ensure scraped_data is a DataFrame before checking `.empty`
    if not isinstance(scraped_data, pd.DataFrame):
        print("⚠️ scraped_data is not a DataFrame! Converting now...")
        scraped_data = pd.DataFrame(scraped_data)

    if scraped_data.empty:
        return jsonify({"message": "No data found"}), 404

    return jsonify({"listings": scraped_data.to_dict(orient="records")}), 200

'''
@app.route("/fetch_data")
def fetch_data():
    """Fetch dummy data (no scraping)."""
    print("🔍 Fetch data request received.", flush=True)
    
    dummy_data = [
        {"VIN": "1234", "Model": "Toyota", "Year": "2022"},
        {"VIN": "5678", "Model": "Honda", "Year": "2021"}
    ]
    
    return jsonify({"listings": dummy_data}), 200

@app.route("/scrape", methods=["GET"])
def scrape():
    """Test if Flask responds instantly."""
    print("🚀 Scraping function called!", flush=True)
    return jsonify({"message": "Scraping test successful!"}), 200
'''
import threading
import pandas as pd
from flask import jsonify

@app.route("/scrape", methods=["GET"])
def scrape():
    """Start scraping in a background thread and return a response immediately."""
    global scraped_data

    def scrape_and_store():
        global scraped_data
        print("🚀 Starting scrape in a separate thread...")

        try:
            scraped_data = scrape_data()  # Fetch scraped data
            
            # 🔍 Debugging: Check what scrape_data() returned
            print(f"📢 Type of scraped_data: {type(scraped_data)}")

            if scraped_data is None:
                print("🚨 scrape_data() returned None! No data available.")
                return
            
            if isinstance(scraped_data, list):
                print("⚠️ scraped_data is a list! Converting to DataFrame...")
                scraped_data = pd.DataFrame(scraped_data)

            print(f"✅ After conversion, type: {type(scraped_data)}")
            print(scraped_data.head())  # Show first few rows

            # Confirm if it's empty safely
            if hasattr(scraped_data, "empty") and scraped_data.empty:
                print("🚨 No data scraped! DataFrame is empty.")

            print(f"✅ Scraping finished. {len(scraped_data)} items retrieved.")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")

    # Start the scrape in a background thread
    thread = threading.Thread(target=scrape_and_store, daemon=True)
    thread.start()

    return jsonify({"message": "Scraping started! Check back soon."}), 200

@app.route("/save_to_db", methods=["POST"])
def save_to_db():
    """Save scraped data to MySQL database."""
    global scraped_data
    conn = connect_db()
    
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_listings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                VIN VARCHAR(255),
                Registration VARCHAR(255),
                Model VARCHAR(255),
                Year VARCHAR(10),
                Engine_Capacity VARCHAR(50),
                Transmission VARCHAR(50),
                Drive_Type VARCHAR(50),
                Fuel VARCHAR(50),
                Cylinders VARCHAR(50),
                No_of_Doors VARCHAR(50),
                Color VARCHAR(50),
                Bidding_Time VARCHAR(255),
                Location VARCHAR(255),
                Views VARCHAR(50),
                Watchers VARCHAR(50),
                Image_URL TEXT
            )
        """)

        for car in scraped_data:
            cursor.execute("""
                INSERT INTO car_listings 
                (VIN, Registration, Model, Year, Engine_Capacity, Transmission, Drive_Type, Fuel, Cylinders, No_of_Doors, Color, Bidding_Time, Location, Views, Watchers, Image_URL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                car.get("VIN", "N/A"), car.get("Registration", "N/A"), car.get("Model", "N/A"), car.get("Year", "N/A"),
                car.get("Engine_Capacity", "N/A"), car.get("Transmission", "N/A"), car.get("Drive_Type", "N/A"),
                car.get("Fuel", "N/A"), car.get("Cylinders", "N/A"), car.get("No_of_Doors", "N/A"),
                car.get("Color", "N/A"), car.get("Bidding_Time", "N/A"), car.get("Location", "N/A"),
                car.get("Views", "0"), car.get("Watchers", "0"), car.get("Image_URL", "")
            ))

        conn.commit()
        return jsonify({"message": "✅ Data saved to database successfully!"}), 200

    except Exception as e:
        print(f"❌ Error saving to database: {e}", flush=True)
        return jsonify({"error": "Failed to save data"}), 500

    finally:
        conn.close()

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 8080))  # Default to 8080
#    app.run(host="0.0.0.0", port=port, debug=False)
