# Nihonium
A bot for the TBGs

### Required Files/Directories
The bot requires three files and one directory not in the repository to run. These files are:
- `pass.txt`, which contains the password for the bots account
- `threadData.json`, a JSON file containing the IDs of the threads the bot can run in, along with the most recently parsed post in each of them. In the format of a dictionary, with each element having a key of the thread's ID (as a string), and a value containing various information about the thread.
- `data.json`, a JSON file containing various statistics. The default is the following: `{"parse_cycles": 0, "commands_parsed": 0, "commands_found": 0, "valid_commands": 0}`
- `logs`, a directory used to store log files. Default is empty.

### `threadData.json`
This file is formatted using the following:
```
{
    "thread_id": {
    	"recentPost": postID,
        "types": [
        	"type1",
            "type2"
        ],
        "name": "The name of the thread",
        "date": {
            "year": year_of_first_post,
            "month": month_of_first_post,
            "day": day_of_first_post,
            "hour": hour_of_first_post,
            "minute": minute_of_first_post,
            "second": second_of_first_post
        }
    }
}
```
##### `"recentPost"`
(Integer) The postID of the most recent post as of the most recent parse-cycle.
##### `"types"`
(List of strings) The categories that the thread is in. Specific categories have addition properties. The default categories are:
```
postID   | The thread is part of the postID family.
postID_0 | Exclusive to postID 0.
2^n      | The thread is part of the 2^n series of postId threads.
3^n      | The thread is part of the 3^n series of postId threads.
fib      | The thread is part of the fibonnaci series of postId threads.
hub      | The thread is considered the bots "hub" thread.
gpostID  | The thread is part of the global postID series of postId threads.
races    | The thread is part of the races series of postId threads.
tbg      | The thread is in the TBGs section of the forum.
rpg      | The thread is in the RPGs section of the forum.
mfg_main | The thread is in the Main Topics section of the forum.
mfg_file | The thread is in the Game Files section of the forum.
```
##### `"name"`
(String) The name of the thread.
##### `"date"`
(Dictonary of integers) The date and time of the first post in the thread.
##### `"goal"`
(Integer) Exclusive to threads with the types `postID` or `gpostID`. The goal post ID.
##### `"race_thread"`
(Integer) Exclusive to threads with the type `races`. The thread ID of the thread being raced against.