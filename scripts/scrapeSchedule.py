import pandas as pd
from datetime import datetime
import os
import sys

def scrape_nfl_schedule(csv_file, season_year, week):
    print(f"Attempting to read CSV file from: {csv_file}")
    if not os.path.exists(csv_file):
        print(f"Error: The file {csv_file} does not exist.")
        return []

    df = pd.read_csv(csv_file)
    
    print("Columns in the CSV file:")
    print(df.columns.tolist())
    
    # Check if required columns are present
    required_columns = ['Week', 'Date', 'Winner/tie', 'Loser/tie', 'PtsW', 'PtsL']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: The following required columns are missing: {missing_columns}")
        return []

    # Convert 'Date' to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter for the specified week
    week_games = df[df['Week'] == week]
    
    # Dictionary to map team names to their three-letter abbreviations
    team_abbr = {
        'Arizona Cardinals': 'crd', 'Atlanta Falcons': 'atl', 'Baltimore Ravens': 'rav',
        'Buffalo Bills': 'buf', 'Carolina Panthers': 'car', 'Chicago Bears': 'chi',
        'Cincinnati Bengals': 'cin', 'Cleveland Browns': 'cle', 'Dallas Cowboys': 'dal',
        'Denver Broncos': 'den', 'Detroit Lions': 'det', 'Green Bay Packers': 'gnb',
        'Houston Texans': 'htx', 'Indianapolis Colts': 'clt', 'Jacksonville Jaguars': 'jax',
        'Kansas City Chiefs': 'kan', 'Las Vegas Raiders': 'rai', 'Los Angeles Chargers': 'sdg',
        'Los Angeles Rams': 'ram', 'Miami Dolphins': 'mia', 'Minnesota Vikings': 'min',
        'New England Patriots': 'nwe', 'New Orleans Saints': 'nor', 'New York Giants': 'nyg',
        'New York Jets': 'nyj', 'Philadelphia Eagles': 'phi', 'Pittsburgh Steelers': 'pit',
        'San Francisco 49ers': 'sfo', 'Seattle Seahawks': 'sea', 'Tampa Bay Buccaneers': 'tam',
        'Tennessee Titans': 'oti', 'Washington Commanders': 'was'
    }
    
    games = []
    for _, row in week_games.iterrows():
        # Check if there's an '@' in the row indicating an away game
        is_away = pd.notna(row.get('Unnamed: 5')) and row['Unnamed: 5'] == '@'
        
        if is_away:
            away_team = row['Winner/tie']
            home_team = row['Loser/tie']
        else:
            home_team = row['Winner/tie']
            away_team = row['Loser/tie']
        
        # Generate the correct URL
        date_str = row['Date'].strftime('%Y%m%d')
        home_team_abbr = team_abbr.get(home_team, '')
        if not home_team_abbr:
            print(f"Warning: Could not find abbreviation for team: {home_team}")
            continue
            
        game_url = f"https://www.pro-football-reference.com/boxscores/{date_str}0{home_team_abbr}.htm"
        
        games.append({
            'Date': row['Date'].strftime('%Y-%m-%d'),
            'Away Team': away_team,
            'Home Team': home_team,
            'Away Score': row['PtsW'] if row['Winner/tie'] == away_team else row['PtsL'],
            'Home Score': row['PtsL'] if row['Winner/tie'] == away_team else row['PtsW'],
            'Winner': 'Away' if row['Winner/tie'] == away_team else 'Home',
            'Game URL': game_url
        })
    
    return games

def main(output_dir, season_year, week):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, '..', 'resources', 'nfl_schedule_2024.csv')
    
    print(f"Full path to CSV file: {csv_file}")
    
    # Convert week to integer
    try:
        week = int(week)
    except ValueError:
        print(f"Error: Invalid week number '{week}'. Please provide a valid integer.")
        return False
    
    games = scrape_nfl_schedule(csv_file, season_year, week)
    
    if not games:
        print(f"No games found for Season {season_year}, Week {week}.")
        return False

    df = pd.DataFrame(games)
    
    if df.empty:
        print("No data to save.")
        return False

    os.makedirs(output_dir, exist_ok=True)
    csv_filename = f"nfl_schedule_{season_year}_week_{week}_{datetime.now().strftime('%Y%m%d')}.csv"
    csv_path = os.path.join(output_dir, csv_filename)
    df.to_csv(csv_path, index=False)
    print(f"Schedule saved to {csv_path}")
    
    print(df)
    
    print(f"\nTotal games: {len(df)}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print("\nGames per team:")
    print(df['Home Team'].value_counts() + df['Away Team'].value_counts())

    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python scrapeSchedule.py <output_dir> <year> <week>")
        sys.exit(1)
    output_dir = sys.argv[1]
    year = int(sys.argv[2])
    week = int(sys.argv[3])
    try:
        success = main(output_dir, year, week)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)