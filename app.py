import mysql.connector
from flask import Flask, render_template, jsonify
import threading
from scrape import scrape_data  # Assuming your scraping function is in scrape.py

app = Flask(__name__)

# Global variable to store scraped data in memory
scraped_data = []

# Database connection function (returns False if connection fails)
def check_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="your_username",
            password="your_password",
            database="car_listings"
        )
        if conn.is_connected():
            print("✅ Database connection successful.")
            return True
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@app.route("/")
def home():
    return render_template("index.html", listings=scraped_data)

@app.route("/fetch_data")
def fetch_data():
    # Log to make sure listings data is available
    print(scraped_data)
    return jsonify({"listings": scraped_data})

@app.route("/scrape", methods=["GET"])
def scrape():
    def scrape_and_store():
        global scraped_data
        scraped_data = scrape_data()  # Assuming this function returns a list of scraped listings
    
    threading.Thread(target=scrape_and_store).start()
    return jsonify({"message": "Scraping started!"}), 200

if __name__ == "__main__":
    print("⏳ Checking database connection...")
    if check_db_connection():
        print("✅ Database connected successfully.")
    else:
        print("⚠️ Database connection failed. Web interface will still be accessible.")

    app.run(debug=False, threaded=False, host="0.0.0.0", port=5000)
