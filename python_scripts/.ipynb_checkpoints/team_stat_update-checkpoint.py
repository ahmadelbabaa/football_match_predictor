import pandas as pd
import numpy as np
import sys
import os

# Check if input is passed
if len(sys.argv) <= 1:
    print("No year provided. Please run the script with a year as an argument.")
    sys.exit(1)  # Exit with an error code

year = sys.argv[1]
current_year = 2025

# File paths
files = {
    'defense' : f'laliga_{year}_defense.csv',
    'gca' : f'laliga_{year}_goal_shot_creation.csv',
    'keeper_adv' : f'laliga_{year}_keeper_adv.csv',
    'shooting' : f'laliga_{year}_shooting.csv',
    'passing' : f'laliga_{year}_passing.csv',
    'passtype' : f'laliga_{year}_pass_types.csv',
    'possession' : f'laliga_{year}_possession.csv',
    'keepers' : f'laliga_{year}_keepers.csv'
}

# Helper function to handle updates
def update_table(file_key, data_folder, table_folder, teams, seasons):
    input_file = os.path.join(data_folder, files[file_key])
    output_file = os.path.join(table_folder, f"{file_key}.csv")
    
    if not os.path.exists(input_file):
        print(f"File {input_file} not found, skipping.")
        return
    
    # Load and process new data
    new_data = pd.read_csv(input_file)
    new_data.rename(columns={'Unnamed: 0': 'id'}, inplace=True)
    new_data.loc[new_data['Team_or_Opponent'] == 'opponent', 'Squad'] = new_data.loc[new_data['Team_or_Opponent'] == 'opponent', 'Squad'].str[3:]
    new_data = pd.merge(new_data, teams[['Squad', 'team_id']], on='Squad', how='left')
    new_data = pd.merge(new_data, seasons, on='Season_End_Year', how='left')
    if file_key == 'keeper_adv':
        new_data.drop(['Season_End_Year', 'Squad', 'Competition_Name','Gender', 'Country', 'Num_Players'], axis=1, inplace=True, errors='ignore')
    else:
        new_data.drop(['Season_End_Year', 'Squad', 'Competition_Name','Gender', 'Country', 'Mins_Per_90', 'Num_Players'], axis=1, inplace=True, errors='ignore')
    

    if year == current_year:
        # update data
        # Update the data for the current year
        if os.path.exists(output_file):
            # Read the existing data
            old_data = pd.read_csv(output_file)
            
            # Update or overwrite rows for the current year
            updated_data = old_data[old_data['season_id'] != new_data['season_id'].iloc[0]]
            updated_data = pd.concat([updated_data, new_data], ignore_index=True)
            
            # Save the updated data back to the file
            updated_data.to_csv(output_file, index=False)
            print(f"Updated {file_key} with new data for the current season (year = '{year}').")
        else:
            # If no file exists, create one with the new data
            new_data.to_csv(output_file, index=False)
            print(f"Created new table for {file_key} with data for the current season (year = '{year}').")
    
    else:
        # Check if already present
        new_year = new_data['season_id'].iloc[0]
        if os.path.exists(output_file):
            old_data = pd.read_csv(output_file)
            if new_year not in old_data['season_id'].unique():
                updated_data = pd.concat([old_data, new_data], ignore_index=True)
                updated_data.to_csv(output_file, index=False)
                print(f"Updated {file_key} with data for season_end_year = '{year}'.")
            else:
                print(f"Data for season_end_year = '{year}' already exists in {file_key}.")
        else:
            new_data.to_csv(output_file, index=False)
            print(f"Created new table for {file_key} with data for season_end_year = '{year}'.")

# Update teams
teams = pd.read_csv("tables/teams.csv")
leagues = pd.read_csv("tables/leagues.csv")


# Update team entries
defense = pd.read_csv(f"data/{files['defense']}")
new_squads = defense.loc[defense['Team_or_Opponent'] == 'team', ['Squad', 'Competition_Name']].drop_duplicates()
new_squads = new_squads[~new_squads['Squad'].isin(teams['Squad'])]

for _, team in new_squads.iterrows():
    team_id = teams.iloc[-1][1]+1
    league_id = leagues.loc[leagues['Competition_Name'] == team['Competition_Name'], 'league_id'].values[0]
    teams = pd.concat([teams, pd.DataFrame({'Squad': [team['Squad']], 'team_id': [team_id], 'league_id': [league_id]})], ignore_index=True)

teams.to_csv("tables/teams.csv", index=False)

# Update seasons
seasons = pd.read_csv("tables/seasons.csv")
season_id = int(year) - 2020
if season_id not in seasons['season_id'].unique():
    seasons = pd.concat([seasons, pd.DataFrame({'season_id': [season_id], 'Season_End_Year': [int(year)]})], ignore_index=True)
    seasons.to_csv("tables/seasons.csv", index=False)

# Update team_season
teams = pd.read_csv('tables/teams.csv')
defense = pd.read_csv(f'data/{files['defense']}')
team_season = defense[['Squad','Season_End_Year','Num_Players','Mins_Per_90']][defense['Team_or_Opponent']=='team']
team_season = pd.merge(team_season,seasons,on=['Season_End_Year'], how='left')
team_season = pd.merge(team_season, teams[['Squad', 'team_id']], on=['Squad'], how='left')
team_season.drop([ 'Season_End_Year', 'Squad'], axis=1, inplace=True)
new_year = team_season.loc[0]['season_id']
old_team_season = pd.read_csv('tables/team_season.csv')
if new_year not in np.array(old_team_season['season_id']):
    team_season = pd.concat([old_team_season, team_season], axis=0, ignore_index=True)
    team_season.to_csv('tables/team_season.csv', index=False)
    print('team_season Updated!')

# Update datasets
for key in files.keys():
    update_table(key, "data", "tables", teams, seasons)
