# Nihonium
A bot for the TBGs

### Required Files
The bot requires three files not in the repository to run. These files are:
- `pass.txt`, which contains the password for the bots account
- `postIDs.json`, a JSON file containing the IDs of the threads the bot can run in, along with the most recently parsed post in each of them. In the format of a dictionary, with each element having a key of the thread's ID (as a string), and a value of the most recent post parsed (as an int, leave this at 0 if you just made the bot or added a new thread)
- `data.json`, a JSON file containing various statistics. The default is the following: ```{"parse_cycles": 0, "commands_parsed": 0, "commands_found": 0, "valid_commands": 0}```