# NFL Stats Webscraper

A Python-based web scraper for collecting NFL game and player statistics from Pro Football Reference for fantasy foorball use.

## Features

- Scrapes weekly NFL game schedules
- Collects detailed player statistics for each game
- Calculates fantasy football points
- Handles rate limiting and retries
- Saves data in CSV format

### Important Note
This project is for research and learning purposes only, not for commercial use. Please respect Pro Football Reference's terms of service and data usage policies.

### Schedule Data Requirements
The project includes the 2024 NFL schedule CSV in the resources directory.

#### Download the season's schedule from Pro Football Reference
Save it as nfl_schedule_YYYY.csv in the resources directory
Ensure it has the required columns: Week, Day, Date, Time, Winner/tie, Loser/tie, PtsW, PtsL

## Installation

1. Clone the repository:

```bash
git clone https://github.com/pmprowse/nflStatsWebscraper.git
cd nflStats-webscrape
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

You can run the scraper in two ways:

### 1. Using the wrapper script (recommended):

```bash
python run_scraper.py <year> <week> [--output directory]
```

Example:

```bash
python run_scraper.py 2024 1 --output my_data
```

### 2. Running individual scripts:

```bash
# First, scrape the schedule
python scripts/scrapeSchedule.py output 2024 1

# Then, scrape player stats
python scripts/scrapeData.py output 2024 1
```

## Data Format

### Schedule Data (`nfl_schedule_{year}_week_{week}_{date}.csv`)

| Column     | Description                             |
| ---------- | --------------------------------------- |
| Date       | Game date (YYYY-MM-DD)                  |
| Away Team  | Visiting team name                      |
| Home Team  | Home team name                          |
| Away Score | Points scored by away team              |
| Home Score | Points scored by home team              |
| Winner     | Which team won ('Home' or 'Away')       |
| Game URL   | Pro Football Reference URL for the game |

### Player Stats Data (`nfl_game_stats_{year}_week_{week}.csv`)

#### Passing Stats

| Column        | Description         |
| ------------- | ------------------- |
| Pass_Cmp      | Completions         |
| Pass_Att      | Attempts            |
| Pass_Yds      | Passing yards       |
| Pass_TD       | Passing touchdowns  |
| Pass_Int      | Interceptions       |
| Pass_Sacks    | Times sacked        |
| Pass_Sack_Yds | Yards lost to sacks |
| Pass_Lng      | Longest pass        |
| Pass_Rate     | Passer rating       |

#### Rushing Stats

| Column   | Description        |
| -------- | ------------------ |
| Rush_Att | Rush attempts      |
| Rush_Yds | Rushing yards      |
| Rush_TD  | Rushing touchdowns |
| Rush_Lng | Longest rush       |

#### Receiving Stats

| Column  | Description          |
| ------- | -------------------- |
| Rec_Tgt | Times targeted       |
| Rec_Rec | Receptions           |
| Rec_Yds | Receiving yards      |
| Rec_TD  | Receiving touchdowns |
| Rec_Lng | Longest reception    |

#### Other Stats

| Column        | Description                             |
| ------------- | --------------------------------------- |
| Player        | Player name                             |
| Team          | Team abbreviation                       |
| Date          | Game date                               |
| Away Team     | Visiting team                           |
| Home Team     | Home team                               |
| Fumbles       | Total fumbles                           |
| Fumbles_Lost  | Fumbles lost                            |
| FantasyPoints | Calculated fantasy points (PPR scoring) |

### Fantasy Points Calculation

Fantasy points are calculated using standard PPR scoring:

- Passing: 0.04 points per yard, 4 points per TD, -2 points per INT
- Rushing: 0.1 points per yard, 6 points per TD
- Receiving: 1 point per reception, 0.1 points per yard, 6 points per TD
- Fumbles: -2 points per fumble lost

## Project Structure

```
nflStats-webscrape/
├── scripts/
│   ├── scrapeSchedule.py
│   └── scrapeData.py
├── resources/
│   └── nfl_schedule_2024.csv
├── output/
│   ├── nfl_schedule_2024_week_*.csv
│   └── nfl_game_stats_2024_week_*.csv
├── run_scraper.py
├── requirements.txt
└── README.md
```

## Notes

- The scraper includes built-in delays to respect Pro Football Reference's rate limits
- All times are in local timezone of the home team
- Team abbreviations follow Pro Football Reference's convention


## Contributing

Feel free to fork and add any addition analyses. 
