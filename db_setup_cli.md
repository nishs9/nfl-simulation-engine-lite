## NFL Sim Engine Lite DB Setup CLI

The `db_setup.py` script is a CLI that can be used to setup the backing DB that is utilized by the NFL Sim Engine.

#### Execution flows:
1. Full DB Hydration (online) -> Retrieves PBP data from data repo and generates the sim engine team stats table
2. Full DB Hydration (local) -> Retrieves the PBP data from a local file and generates the sim engine team stats table. This is meant to be a backup option if we aren't able to generate the data via the online flow

#### Options:
1. (-l) --local: This is how we will denote the local db hydration flow
2. (-r) --save_raw_pbp: This flag can be used to tell the program to save the full play-by-play data as a CSV
3. (-f) --save_filtered_pbp

#### More on local DB hydration
