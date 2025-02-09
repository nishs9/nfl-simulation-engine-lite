## NFL Sim Engine Lite DB Setup CLI

The `db_setup.py` script is a CLI that can be used to setup the backing DB that is utilized by the NFL Sim Engine. You run the script from the `utils` folder. It will generated a file called `nfl_stats.db` in the same directory. Move this file to the `src` folder to complete the setup of the DB.

#### Execution flows:
1. Full DB Hydration (online) -> Retrieves PBP data from the online data repo and generates the sim engine team stats table
2. Full DB Hydration (local) -> Retrieves the PBP data from a local file and generates the sim engine team stats table. This is meant to be a backup option if we aren't able to generate the data via the online flow

#### Options:
1. (-l) --local: This is the flag to run the db hydration flow script using a raw CSV saved in the `input` folder
2. (-r) --save_raw_pbp: This flag can be used to tell the program to save the full play-by-play data as a CSV
3. (-f) --save_filtered_pbp: This flag can be used to tell the program to save the filtered play-by-play data that is used for calculating team statistics used in the simulation engine.

#### More on local DB hydration
Local DB hydration is just meant to be a fallback flow in case there is some issue with accessing the data repo via the script. In order to setup the DB using local files, simply go to https://github.com/nflverse/nflverse-data/releases and find the `pbp` folder. Then download the CSV for 2024 play-by-play data and put it in the `input` folder. You can now run the setup script in local mode and hydrate the DB.
