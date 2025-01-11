import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import sys
import glob

def scrape_game_data(game_url, session, max_retries=5, initial_delay=1):
    for attempt in range(max_retries):
        try:
            response = session.get(game_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'player_offense'})
            
            if not table:
                print(f"No table found on page: {game_url}")
                return None

            all_data = []
            rows = table.find_all('tr')

            for row in rows:
                if row.find('th', {'scope': 'col'}) is not None:
                    continue
                
                player_cell = row.find('th', {'data-stat': 'player'})
                if not player_cell:
                    continue

                cols = row.find_all(['td', 'th'])
                
                if len(cols) < 22:
                    print(f"Unexpected number of columns ({len(cols)}) for player {player_cell.text.strip()} on page {game_url}")
                    continue

                stats = {
                    'Player': player_cell.text.strip(),
                    'Team': cols[1].text.strip(),
                    'Pass_Cmp': cols[2].text.strip() or '0',
                    'Pass_Att': cols[3].text.strip() or '0',
                    'Pass_Yds': cols[4].text.strip() or '0',
                    'Pass_TD': cols[5].text.strip() or '0',
                    'Pass_Int': cols[6].text.strip() or '0',
                    'Pass_Sacks': cols[7].text.strip() or '0',
                    'Pass_Sack_Yds': cols[8].text.strip() or '0',
                    'Pass_Lng': cols[9].text.strip() or '0',
                    'Pass_Rate': cols[10].text.strip() or '0',
                    'Rush_Att': cols[11].text.strip() or '0',
                    'Rush_Yds': cols[12].text.strip() or '0',
                    'Rush_TD': cols[13].text.strip() or '0',
                    'Rush_Lng': cols[14].text.strip() or '0',
                    'Rec_Tgt': cols[15].text.strip() or '0',
                    'Rec_Rec': cols[16].text.strip() or '0',
                    'Rec_Yds': cols[17].text.strip() or '0',
                    'Rec_TD': cols[18].text.strip() or '0',
                    'Rec_Lng': cols[19].text.strip() or '0',
                    'Fumbles': cols[20].text.strip() or '0',
                    'Fumbles_Lost': cols[21].text.strip() or '0'
                }
                
                all_data.append(stats)
            
            return all_data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                delay = initial_delay * (2 ** attempt)
                print(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"HTTP error occurred: {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving page {game_url}: {e}")
            return None

    print(f"Max retries reached for {game_url}")
    return None

def clean_data(df):
    numeric_columns = ['Pass_Cmp', 'Pass_Att', 'Pass_Yds', 'Pass_TD', 'Pass_Int', 'Pass_Sacks', 
                       'Pass_Sack_Yds', 'Pass_Lng', 'Rush_Att', 'Rush_Yds', 'Rush_TD', 
                       'Rush_Lng', 'Rec_Tgt', 'Rec_Rec', 'Rec_Yds', 'Rec_TD', 'Rec_Lng', 
                       'Fumbles', 'Fumbles_Lost']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            print(f"Warning: Column '{col}' not found in the DataFrame")
    
    if 'Pass_Rate' in df.columns:
        df['Pass_Rate'] = pd.to_numeric(df['Pass_Rate'], errors='coerce').fillna(0.0).astype(float)
    else:
        print("Warning: Column 'Pass_Rate' not found in the DataFrame")
    
    return df

def main(output_dir, year, week):
    # Find the most recent schedule file for the specified year and week
    schedule_files = glob.glob(os.path.join(output_dir, f'nfl_schedule_{year}_week_{week}*.csv'))
    if not schedule_files:
        print(f"No schedule file found for Year {year}, Week {week}. Please run scrapeSchedule.py first.")
        return
    
    latest_schedule = max(schedule_files, key=os.path.getctime)
    print(f"Using schedule file: {latest_schedule}")

    # Read the schedule CSV file
    schedule_df = pd.read_csv(latest_schedule)
    
    # Create a session object
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    all_data = []
    total_games = len(schedule_df)

    for index, row in schedule_df.iterrows():
        game_url = row['Game URL']
        game_date = row['Date']
        away_team = row['Away Team']
        home_team = row['Home Team']
        
        print(f"Scraping data for game {index + 1} of {total_games}: {away_team} @ {home_team} on {game_date}...")
        
        game_data = scrape_game_data(game_url, session)
        if game_data:
            for player_data in game_data:
                player_data['Date'] = game_date
                player_data['Away Team'] = away_team
                player_data['Home Team'] = home_team
            all_data.extend(game_data)
            print(f"Data scraped successfully for {away_team} @ {home_team}")
        else:
            print(f"Failed to scrape data for {away_team} @ {home_team}")
        
        # Random delay between requests
        time.sleep(random.uniform(3, 7))

    if not all_data:
        print("No data was scraped. Check if the URLs are correct and if the website structure has changed.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Clean the data
    df = clean_data(df)

    # Save to CSV
    output_filename = os.path.join(output_dir, f'nfl_game_stats_{year}_week_{week}.csv')
    df.to_csv(output_filename, index=False)
    print(f"Data saved to {output_filename}")

    # Calculate fantasy points
    if all(col in df.columns for col in ['Pass_Yds', 'Pass_TD', 'Pass_Int', 'Rush_Yds', 'Rush_TD', 'Rec_Rec', 'Rec_Yds', 'Rec_TD', 'Fumbles_Lost']):
        df['FantasyPoints'] = (
            df['Pass_Yds'] * 0.04 +
            df['Pass_TD'] * 4 +
            df['Pass_Int'] * -2 +
            df['Rush_Yds'] * 0.1 +
            df['Rush_TD'] * 6 +
            df['Rec_Rec'] * 1 +  # PPR
            df['Rec_Yds'] * 0.1 +
            df['Rec_TD'] * 6 +
            df['Fumbles_Lost'] * -2
        )

        print("\nTop 10 players by fantasy points:")
        print(df[['Date', 'Player', 'Team', 'FantasyPoints']].sort_values('FantasyPoints', ascending=False).head(10))

    # Print some summary statistics
    print("\nTotal fantasy points by team:")
    print(df.groupby('Team')['FantasyPoints'].sum().sort_values(ascending=False))

    print("\nTop passers:")
    print(df.sort_values('Pass_Yds', ascending=False)[['Date', 'Player', 'Team', 'Pass_Yds', 'Pass_TD', 'Pass_Int']].head())

    print("\nTop rushers:")
    print(df.sort_values('Rush_Yds', ascending=False)[['Date', 'Player', 'Team', 'Rush_Att', 'Rush_Yds', 'Rush_TD']].head())

    print("\nTop receivers:")
    print(df.sort_values('Rec_Yds', ascending=False)[['Date', 'Player', 'Team', 'Rec_Tgt', 'Rec_Rec', 'Rec_Yds', 'Rec_TD']].head())

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python scrapeData.py <output_dir> <year> <week>")
        sys.exit(1)
    output_dir = sys.argv[1]
    year = int(sys.argv[2])
    week = int(sys.argv[3])
    main(output_dir, year, week)