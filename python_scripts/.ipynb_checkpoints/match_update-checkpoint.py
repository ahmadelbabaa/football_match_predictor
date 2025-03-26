import sys
import pandas as pd
import numpy as np

# Check if input is passed
if len(sys.argv) <= 1:
    print("No year provided. Please run the script with a year as an argument.")
    sys.exit(1)  # Exit with an error code

year = sys.argv[1]

try:
    # Load new match data
    matches_file = f'match_results_big5_{year}.csv'
    new_matches = pd.read_csv(f'data/{matches_file}')
    new_matches.drop(
        ['Unnamed: 0', 'Gender', 'Country', 'Round', 'Venue', 'Referee', 
         'Notes', 'Attendance', 'MatchURL'], 
        axis=1, inplace=True, errors='ignore'
    )
except FileNotFoundError:
    print(f"Error: File {matches_file} not found in the 'data' folder.")
    sys.exit(1)

# Load auxiliary tables
seasons = pd.read_csv('tables/seasons.csv')
leagues = pd.read_csv('tables/leagues.csv')
teams = pd.read_csv('tables/teams.csv')

# Merge data with additional information
new_matches = pd.merge(new_matches, seasons, on=['Season_End_Year'], how='left')
new_matches = pd.merge(new_matches, leagues, on=['Competition_Name'], how='left')
new_matches.drop(['Season_End_Year', 'Competition_Name'], axis=1, inplace=True)

# Add home_id and away_id
new_matches = pd.merge(new_matches, teams[['Squad', 'team_id']], left_on='Home', right_on='Squad', how='left')
new_matches.rename(columns={'team_id': 'home_id'}, inplace=True)
new_matches = pd.merge(new_matches, teams[['Squad', 'team_id']], left_on='Away', right_on='Squad', how='left')
new_matches.rename(columns={'team_id': 'away_id'}, inplace=True)
new_matches.drop(['Home', 'Away', 'Squad_x', 'Squad_y'], axis=1, inplace=True)

# Set match results
conditions = [
    new_matches['HomeGoals'] == new_matches['AwayGoals'],
    new_matches['HomeGoals'] < new_matches['AwayGoals'],
    new_matches['HomeGoals'] > new_matches['AwayGoals']
]
choices = ['x', 2, 1]
new_matches['result'] = np.select(conditions, choices, default=None)

# Load existing matches
matches = pd.read_csv('tables/matches.csv')

# Ensure 'home_id' and 'Date' columns exist
for df, name in [(matches, "matches"), (new_matches, "new_matches")]:
    if 'home_id' not in df.columns or 'Date' not in df.columns:
        raise KeyError(f"Columns 'home_id' and 'Date' must exist in the {name} dataset.")

# Convert 'Date' to datetime
matches['Date'] = pd.to_datetime(matches['Date'], errors='coerce')
new_matches['Date'] = pd.to_datetime(new_matches['Date'], errors='coerce')

# Create unique match keys
matches['match_key'] = matches['home_id'].astype(str) + '_' + matches['Date'].astype(str)
new_matches['match_key'] = new_matches['home_id'].astype(str) + '_' + new_matches['Date'].astype(str)

# Filter new matches
unique_matches = new_matches[~new_matches['match_key'].isin(matches['match_key'])]

# Append unique matches
num_row_uploaded = len(unique_matches)
if num_row_uploaded > 0:
    matches = pd.concat([matches, unique_matches], axis=0, ignore_index=True)

# Save updated matches
matches.to_csv('tables/matches.csv', index=False)

print(f"Uploaded {num_row_uploaded} rows!")
