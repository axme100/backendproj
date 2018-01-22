# Spanlib

This project aims to create a pedagogical web applciation for creating Mad Libs in the Spanish language classroom or by students of Spanish and other languages around the world.

## Initializing the database and adding samaple entries

To get started, first fork and clone this repository. In the terminal run:
```
python3 database_setup.py
python3 add_samples.py
```
The first command will set up and configue the database and the second command will add some examples entries to it.

## Adding your Google API credentials. 
You will need to add your Google API credentials as a file named client_secrets.json to the working directory. As of now, the only way to login to this app (which is needed to create a Mad Lib is through the Google OAuth API)

