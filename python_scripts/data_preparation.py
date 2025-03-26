import pandas as pd

# Read in the datasets
match = pd.read_csv('tables/matches.csv')
team_season = pd.read_csv('tables/team_season.csv')
defense = pd.read_csv('tables/defense.csv')
passing = pd.read_csv('tables/passing.csv')
gca = pd.read_csv('tables/gca.csv')
keeper_adv = pd.read_csv('tables/keeper_adv.csv')
keepers = pd.read_csv('tables/keepers.csv')
shooting = pd.read_csv('tables/shooting.csv')
passtype = pd.read_csv('tables/passtype.csv')
possession = pd.read_csv('tables/possession.csv')
teams = pd.read_csv('tables/teams.csv')
seasons = pd.read_csv('tables/seasons.csv')



teams_stat = pd.merge(team_season,teams, on=['team_id'], how='left')

teams_stat = pd.merge(teams_stat, defense, on=['team_id', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat,gca, on=['team_id', 'Team_or_Opponent', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat,keepers, on=['team_id', 'Team_or_Opponent', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat,keeper_adv, on=['team_id', 'Team_or_Opponent', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat,shooting, on=['team_id', 'Team_or_Opponent', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat,passing, on=['team_id', 'Team_or_Opponent', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat,passtype, on=['team_id', 'Team_or_Opponent', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat,possession, on=['team_id', 'Team_or_Opponent', 'season_id'], how='left')
teams_stat.drop('id', axis=1, inplace=True)

teams_stat = pd.merge(teams_stat, seasons[['season_id','Season_End_Year']], on='season_id', how='left')
teams_stat['next_season_end'] = teams_stat['Season_End_Year']+1
teams_stat = pd.merge(teams_stat, seasons, left_on='next_season_end', right_on='Season_End_Year', how='left')
teams_stat.drop('Season_End_Year_y', axis=1, inplace=True)
teams_stat.rename(columns={'season_id_y': 'next_season_id', 'season_id_x': 'season_id', 'Season_End_Year_x': 'Season_End_Year'}, inplace=True)

# teams_stat.to_csv('tables/team_stat.csv', index=False)

###########################################################################################################################

team_stat = pd.read_csv('tables/team_stat.csv')

# Drop unnecessary columns
match.drop(['Day', 'Date', 'HomeGoals','AwayGoals','match_id','league_id','Country'], axis=1, inplace=True)

# Merge the match and team_stat dataframes
data = pd.merge(match, team_stat, left_on=['home_id', 'season_id'], right_on=['team_id', 'next_season_id'], how='left')
data = data[data['Team_or_Opponent'] != 'opponent']
data.drop(['season_id_y', 'team_id', 'next_season_end', 'next_season_id', 'Team_or_Opponent'], axis=1, inplace=True)
data.rename(columns={'season_id_x': 'season_id'}, inplace=True)

# Rename columns for away team data
team_stat_renamed = team_stat.rename(columns={col: f"{col}_away" for col in team_stat.columns})

# Merge the away data
data = pd.merge(data, team_stat_renamed, left_on=['away_id', 'season_id'], right_on=['team_id_away', 'next_season_id_away'], how='left')
data = data[data['Team_or_Opponent_away'] != 'team']
data.drop(['season_id_away', 'team_id_away', 'next_season_end_away', 'next_season_id_away', 'Team_or_Opponent_away'], axis=1, inplace=True)
data.rename(columns={'season_id_x': 'season_id'}, inplace=True)

# Clean the data
data.dropna(subset=['Num_Players'])
data.drop(['season_id', 'match_key', 'Squad', 'league_id', 'Squad_away', 'league_id_away', 'Season_End_Year_away', 'Time', 'Home_xG', 'Away_xG'], axis=1, inplace=True)

# Save the cleaned data to a CSV file
data.to_csv('tables/data.csv', index=False)

# Print status message
print("Script executed successfully. Data saved to 'tables/data.csv'.")