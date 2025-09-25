import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

# The target URL for NFL standings from ESPN
URL = "https://www.espn.com/nfl/standings"

# Initialize Flask App
app = Flask(__name__)
# Enable CORS to allow the HTML page to fetch data from this server
CORS(app)

def scrape_nfl_standings():
    """
    Scrapes the NFL standings from ESPN and returns a structured dictionary.
    """
    try:
        # Use headers to mimic a browser visit
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        page = requests.get(URL, headers=headers)
        page.raise_for_status()

        soup = BeautifulSoup(page.content, "html.parser")
        
        standings = {'AFC': [], 'NFC': []}
        
        # Find the two tables for AFC and NFC
        tables = soup.find_all('table', class_='standings')

        if not tables or len(tables) < 2:
            return None # Return None if tables aren't found

        conference_names = ['AFC', 'NFC']
        for i, table in enumerate(tables):
            conference = conference_names[i]
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                # Team names are in a specific span within the first cell
                team_name_tag = row.find('span', class_='hide-mobile')
                if team_name_tag:
                    team_name = team_name_tag.text.strip()
                    
                    # Stats are in the subsequent cells
                    stats = row.find_all('td')
                    if len(stats) > 3:
                        wins = stats[1].text.strip()
                        losses = stats[2].text.strip()
                        ties = stats[3].text.strip()
                        
                        standings[conference].append({
                            'team': team_name,
                            'record': f"{wins}-{losses}-{ties}"
                        })
        return standings

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None

# Define an API endpoint that will trigger the scraper
@app.route('/api/nfl-standings')
def get_standings():
    data = scrape_nfl_standings()
    if data:
        # Return the scraped data as a JSON response
        return jsonify(data)
    else:
        # Return an error message if scraping fails
        return jsonify({"error": "Failed to scrape data"}), 500

# This allows the script to be run directly
if __name__ == "__main__":
    # Runs the server on http://127.0.0.1:5000
    app.run(debug=True)
