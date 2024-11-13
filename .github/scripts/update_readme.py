import requests
import re
import pytz
from datetime import datetime

# Constants for README markers
START_STANDINGS_MARKER = "<!-- START_LALIGA_STANDINGS -->"
END_STANDINGS_MARKER = "<!-- END_LALIGA_STANDINGS -->"
START_NEXT_MATCH_MARKER = "<!-- START_NEXT_MATCH -->"
END_NEXT_MATCH_MARKER = "<!-- END_NEXT_MATCH -->"
README_PATH = "README.md"

# API constants
LIGA_STANDINGS_URL = "https://api.football-data.org/v4/competitions/PD/standings"
NEXT_MATCH_URL = "https://api.football-data.org/v4/teams/81/matches"  # FC Barcelona
API_KEY = "b6f45dd8ebea43a7bfea492687b72550"  # Replace with your actual API key

def convert_to_swedish_time(utc_date, is_first_match):
    # Parse the UTC date string to a datetime object
    utc_time = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
    
    # Set the UTC timezone to the datetime object
    utc_time = pytz.utc.localize(utc_time)
    
    # Convert the UTC time to Swedish time (Europe/Stockholm)
    stockholm_tz = pytz.timezone('Europe/Stockholm')
    swedish_time = utc_time.astimezone(stockholm_tz)
    
    # Return the formatted time
    if is_first_match:
        return f"{swedish_time.strftime('%Y-%m-%d')}<br>{swedish_time.strftime('%H:%M:%S')}"
    else:
        return f"{swedish_time.strftime('%Y-%m-%d')}"

# Fetch La Liga standings
def fetch_liga_standings():
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(LIGA_STANDINGS_URL, headers=headers)
    data = response.json()

    # Get top 5 teams for example
    top_teams = data['standings'][0]['table'][:4]
    
    # Generate Markdown table
    
    
    table = "Position | Team | Matches | Won | Draw | Lost | Points\n"
    table += "|---------|------|---------|-----|------|------|-------|\n"
    for team in top_teams:
        position = team['position']
        name = team['team']['name']
        points = team['points']
        won = team['won']
        draw = team['draw']
        lost = team['lost']
        matches = team['playedGames']
        crest_url = team['team']['crest']
        
        if name.lower() == "fc barcelona":
            crest = f"<img src='{crest_url}' alt='{name} crest' width='20' height='20' style='vertical-align: middle;'> **{name}**"
            table += f"| **{position}** | {crest} | **{matches}** | **{won}** | **{draw}** | **{lost}** | **{points}** |\n"
        else:
            crest = f"<img src='{crest_url}' alt='{name} crest' width='20' height='20' style='vertical-align: middle;'> {name}"
            table += f"| {position} | {crest} | {matches} | {won} | {draw} | {lost} | {points} |\n"
    
    return table

# Fetch FC Barcelona's next match
def get_next_match():
    url = "https://api.football-data.org/v4/teams/81/matches"
    headers = {
        'X-Auth-Token': 'b6f45dd8ebea43a7bfea492687b72550'  # Replace with your API key
    }
    
    params = {
        'status': 'SCHEDULED',  # Only fetch scheduled matches
        'limit': 3  # Limit to the next 3 matches
    }
    
    # Make the API request
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    matches = data['matches']
    is_first_match = True

    table = "Home Team | Away Team | Matchday | Competition \n"
    table += "|----------------|------|-------|--| \n"
    # Extract the relevant match details
    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        date = convert_to_swedish_time(match['utcDate'], is_first_match)
        competition = match['competition']['name']
        home_crest_url = match['homeTeam']['crest']
        away_crest_url = match['awayTeam']['crest']

        home_crest = f"<img src='{home_crest_url}' alt='{date} crest' width='100' height='100' style='vertical-align: middle;'>"
        away_crest = f"<img src='{away_crest_url}' alt='{date} crest' width='100' height='100' style='vertical-align: middle;'>"
        home_name = f"<br>**{home_team}**"
        away_name = f"<br>**{away_team}**"

        if is_first_match:
            table += f"| {home_crest} {home_name} | {away_crest} {away_name} | **{date}** | **{competition}** \n"
            is_first_match = False
        else:
            table += f"| {home_team} | {away_team} | {date} | {competition} \n"

    table += f"\n Last updated {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}"
    return table

# Update README file
def update_readme():
    standings_table = fetch_liga_standings()
    next_match_info = get_next_match()

    # Read the README content
    with open(README_PATH, "r") as file:
        readme_content = file.read()

    # Update standings section
    updated_standings_content = f"{START_STANDINGS_MARKER}\n{standings_table}\n{END_STANDINGS_MARKER}"
    updated_content = re.sub(
        f"{START_STANDINGS_MARKER}.*?{END_STANDINGS_MARKER}",
        updated_standings_content,
        readme_content,
        flags=re.DOTALL
    )

    # Update next match section
    updated_next_match_content = f"{START_NEXT_MATCH_MARKER}\n{next_match_info}\n{END_NEXT_MATCH_MARKER}"
    updated_content = re.sub(
        f"{START_NEXT_MATCH_MARKER}.*?{END_NEXT_MATCH_MARKER}",
        updated_next_match_content,
        updated_content,
        flags=re.DOTALL
    )

    # Write the updated content back to README.md
    with open(README_PATH, "w") as file:
        file.write(updated_content)

if __name__ == "__main__":
    update_readme()
    print("README.md updated with the latest La Liga standings and next match information.")
