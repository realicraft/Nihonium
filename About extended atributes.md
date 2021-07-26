# Extended Attributes
Extended attributes are attributes exclusive to Flerovium. They're used to let Flerovium know:
* if the copy of ```commands.py``` supports Flerovium
* what commands that Flerovium didn't support
* if Flerovium can use custom functions that allows fancy Discord-related posts/commands (or something)
## List of extended attributes
### ```flerovium_minver```
This behaves similar to ```nihonium_minver```.
### ```flerovium_compatible```
This defines the overall compatibility with Flerovium.
### ```flerovium_commands```
This defines Flerovium-exclusive functions. These functions takes priority over Nihonium functions in Flerovium.
### ```flerovium_inc_commands```
This defines functions that are not supported by Flerovium.
### ```bot_data["is_flerovium"]```
This tells commands.py if Flerovium is using it. 
