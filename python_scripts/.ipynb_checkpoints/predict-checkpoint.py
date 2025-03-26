import numpy as np
import pandas as pd
import xgboost as xgb
import pickle
import sys

# Get input arguments from the command line (these will come from the Tkinter UI)
home_team = sys.argv[1]
away_team = sys.argv[2]
match_week = sys.argv[3]
season_end_year = int(sys.argv[4])

# Load necessary datasets
team_stat = pd.read_csv('tables/team_stat.csv')
teams = pd.read_csv('tables/teams.csv')
seasons = pd.read_csv('tables/seasons.csv')

# Prepare match data based on the input
match_data = {
    'Wk': [int(match_week)],
    'home_team': [home_team],
    'away_team': [away_team],
    'season_end_year': [season_end_year]
}

match_data = pd.DataFrame(match_data)

# Merge with teams data to get team IDs for home team
match_data = pd.merge(match_data, teams[['Squad', 'team_id']], left_on=['home_team'], right_on=['Squad'], how='left')

match_data = match_data.rename(columns={'team_id': 'home_id'})
match_data.drop(['Squad', 'home_team'], axis=1, inplace=True)

# Merge with teams data to get team IDs for away team
match_data = pd.merge(match_data, teams[['Squad', 'team_id']], left_on=['away_team'], right_on=['Squad'], how='left')

match_data = match_data.rename(columns={'team_id': 'away_id'})
match_data.drop(['Squad', 'away_team'], axis=1, inplace=True)

# Merge with seasons data to get season IDs
match_data = pd.merge(match_data, seasons[['Season_End_Year', 'season_id']], left_on=['season_end_year'], right_on=['Season_End_Year'], how='left')
match_data.drop(['Season_End_Year', 'season_end_year'], axis=1, inplace=True)

# Merge with team statistics for home team
match_data = pd.merge(match_data, team_stat, left_on=['home_id', 'season_id'], right_on=['team_id', 'next_season_id'], how='left')
match_data = match_data[match_data['Team_or_Opponent'] != 'opponent']
match_data.drop(['season_id_y', 'team_id', 'next_season_end', 'next_season_id', 'Team_or_Opponent'], axis=1, inplace=True)
match_data.rename(columns={'season_id_x': 'season_id'}, inplace=True)

# Merge with team statistics for away team
team_stat_renamed = team_stat.rename(columns={col: f"{col}_away" for col in team_stat.columns})
match_data = pd.merge(match_data, team_stat_renamed, left_on=['away_id', 'season_id'], right_on=['team_id_away', 'next_season_id_away'], how='left')
match_data = match_data[match_data['Team_or_Opponent_away'] != 'team']
match_data.drop(['season_id_away', 'team_id_away', 'next_season_end_away', 'next_season_id_away', 'Team_or_Opponent_away'], axis=1, inplace=True)
match_data.rename(columns={'season_id_x': 'season_id'}, inplace=True)

# Drop unnecessary columns
match_data = match_data.drop(['Competition_Name', 'Gender', 'Country', 'Gender_away', 'Country_away', 'Competition_Name_away', 'Mins_Per_90_x', 'Mins_Per_90_x_away'], axis=1)
match_data = match_data.drop(['season_id', 'Squad', 'league_id', 'Squad_away', 'league_id_away', 'Season_End_Year', 'Season_End_Year_away'], axis=1)

# Encode categorical variables (team IDs)
with open('home_encoder.pkl', 'rb') as file:
    home_encoder = pickle.load(file)
encoded_home = home_encoder.transform(match_data['home_id'])

with open('away_encoder.pkl', 'rb') as file:
    away_encoder = pickle.load(file)
encoded_away = away_encoder.transform(match_data['away_id'])

match_data['home_id'] = encoded_home
match_data['away_id'] = encoded_away

# Handle missing values
if match_data.isnull().sum().sum() > 0:
    print('Impossible to predict the match result due to lack of data. One of the 2 squads did not play in the major league last year!')
    sys.exit(1)

#import model and predict
model = xgb.XGBClassifier()
model.load_model('xgboost_model.json')

with open('y_encoder.pkl', 'rb') as file:
    loaded_encoder = pickle.load(file)


# match_data = xgb.DMatrix(match_data, enable_categorical=True)
pred_proba = model.predict_proba(match_data)
pred = np.argmax(pred_proba)
target_names = loaded_encoder.classes_

pred = target_names[pred]

# Ensure the prediction result is handled properly
# Print the result (this model can make mistakes)
if pred == 'x':
    print(f'The match will end in a draw.')
elif pred == '1':
    print(f'{home_team} will win the match.')
else:
    print(f'{away_team} will win the match.')

# Print probabilities for each class
for i, prob in enumerate(pred_proba[0]):  # Assuming match_data contains one row of input
    print(f"Class: {target_names[i]}, Probability: {prob*100:.1f}%")

# Print model caution message
print("\n\nThe model can make mistakes. Its output should be interpreted with caution and is not intended as professional advice or absolute truth.")
