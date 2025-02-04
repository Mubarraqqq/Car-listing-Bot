# Car Listings Scraper & Web Interface

## Overview
This project is a web application that scrapes car listings from an online auction site and stores them in a MySQL database. The scraped data is also displayed via a Flask-based web interface.

## Features
- **Web Scraping**: Automates data extraction from car listing websites.
- **Database Integration**: Stores scraped listings in a MySQL database.
- **Web Interface**: Provides a user-friendly interface to view listings.
- **Threaded Scraping**: Allows scraping to run asynchronously in the background.

## Technologies Used
- **Flask** - Backend web framework
- **Selenium** - Web scraping automation
- **MySQL** - Database storage
- **Requests** - API communication
- **Threading** - Background task management

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.7+
- MySQL Server
- WebDriver (Edge recommended for Selenium)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up MySQL database:
   - Create a database named `car_listings`.
   - Update `scrape.py` and `app.py` with your database credentials.

4. Set up Selenium WebDriver:
   - Install Edge WebDriver (or modify for Chrome/Firefox).

## Usage
### Running the Web App
```sh
python app.py
```
Navigate to `http://127.0.0.1:5000/` in your browser.

### Scraping Listings
1. Start the web app.
2. Visit `http://127.0.0.1:5000/scrape` to trigger scraping.
3. Data is stored in the database and sent to the web interface.

### API Endpoints
#### `/fetch_data` (GET)
- **Response**: Returns all stored car listings as JSON.

#### `/scrape` (GET)
- **Triggers**: Background scraping of car listings.
- **Response**: `{ "message": "Scraping started!" }`

## Notes & Limitations
- Ensure WebDriver is properly installed and configured.
- Some listing sites may block frequent scraping; use delays if necessary.
- Replace database credentials before deployment.

## License
This project is under the MIT License.

## Contributors
- **Your Name** - [GitHub Profile](https://github.com/mubarraqqq/)

