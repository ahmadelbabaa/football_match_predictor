# football_match_predictor

In order to facilitate teh replicability of the process, here there is a description on how to proceed.

Because the folder with the tables is complete, in order to replicate the process I suggest to make a copy of the folder with all the notebooks and clear the tables folder in one of them. In this way it is possible to build the database from scratch. (important leave the data folder full, as contains the data to build the database)

Then open the 'database_creation_match.ipynb' and 'database_create_team_stats.ipynb' notebooks and run through them. These file will create all th relevan tables in the tables folder.

Once the tables are built then it is possible to work from the UI.
So oprn teh 'User_Interfaces.ipynb' notebook wher all the Ui are collected.
From there you can updat the tables with the data of following seasons (in the creation of the tables data relative to the season end year 2020 were uploaded, so the data that can be uploaded is the one about years 2021,2022,2023 and 2024). If more information about the procedure of uploading that are needed have a look at the 'database_update_matches.ipynb' and 'database_updat_team_stats.ipynb' notebooks.

Then it is possible to extract the 'data' table (using the relative UI), which is the one used to train the model. In oreder to see teh code relative to the data extraction look at 'data_extraction_fron_database.ipynb' notebook.
While in order to analyze the code of the training of the model have a look at the 'model.ipynb' notebook.

And finally it is possible to make predictions using teh prediction UI.