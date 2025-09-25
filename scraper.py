import requests
from bs4 import BeautifulSoup
import json

# The target URL for NFL standings from ESPN
URL = "https://www.espn.com/nfl/standings"

def scrape_nfl_standings():
    """
    Scrapes the NFL standings from ESPN and returns a structured dictionary.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        page = requests.get(URL, headers=headers)
        page.raise_for_status()

        soup = BeautifulSoup(page.content, "html.parser")
        
        standings = {'AFC': [], 'NFC': []}
        
        tables = soup.find_all('table', class_='standings')

        if not tables or len(tables) < 2:
            print("Error: Standings tables not found.")
            return None

        conference_names = ['AFC', 'NFC']
        for i, table in enumerate(tables):
            conference = conference_names[i]
            # Find all rows in the table body, which contains team data
            for row in table.find('tbody').find_all('tr'):
                team_name_tag = row.find('span', class_='hide-mobile')
                if team_name_tag:
                    team_name = team_name_tag.text.strip()
                    # All stats (W-L-T) are in separate `td` elements
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
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    scraped_data = scrape_nfl_standings()
    
    if scraped_data:
        # Save the data to a file named 'standings.json'
        with open('standings.json', 'w') as f:
            json.dump(scraped_data, f, indent=4)
        print("Successfully scraped data and saved to standings.json")
    else:
        print("Failed to scrape data.")
