import random, math, datetime, time, sys, os, versions, shutil, json
from lxml import html

# This file is used to define the commands used by Nihonium.

__version__ = versions.Version(1, 3, 1)     # This defines the version of the module's framework.
version = versions.Version(1, 7, 5)         # This defines the version of the user-added commands.
nihonium_minver = versions.Version(0, 9, 0) # This defines the minimum version of Nihonium needed to run these commands.
alt_minvers = {"nihonium2": versions.Version(0, 9, 0)} # Used to define minimum versions for other bots. Format: {"<id>": versions.Version(<version>)}

def logEntry(entry: str, timestamp=None): # Used to add entries to the log files.
    if timestamp is None: timestamp = datetime.datetime.now()
    with open("logs/" + timestamp.strftime("%Y%m%d") + ".log", "a", encoding="utf-8") as logfile:
        logfile.write("[" + timestamp.strftime("%I:%M:%S.%f %p") + "] " + entry + "\n")

# Commands can take any number of placement arguments and should return a string containing the output of the command. (Beginning/Trailing newline not required.)
# Commands can take inputs that are Integers, Floats, Strings, and Booleans. 
# If a command raises TypeError, ValueError, KeyError, IndexError, OverflowError, or ZeroDivisionError, it will be caught by Nihonium. Other errors will not be caught.
# The first argument a command recieves will contain information about the bot.
# The second argument a command recieves will contain information about the thread the command was called in.
# The third argument a command recieves will contain information about the user who called the command.

# Add commands below here.
#-------------------------
def coin(bot_data, thread_data, user_data):
    return "You flip a coin, and get " + random.choice(["heads", "tails"]) + "."

def coin2(bot_data, thread_data, user_data):
    return "You flip a coin 2, and get " + random.choice(["heads 2", "tails 2"]) + "."

def dice(bot_data, thread_data, user_data, num=1, size=20):
    num = int(float(num))
    size = int(float(size))
    hold = []
    doSanity = False # sanity check, prevent the post from getting too long
    if (num < 0): return "You can't roll negative dice."
    elif (num == 0): return "You roll no dice, and get nothing."
    elif (size < 0): return "You can't roll something that doesn't exist."
    elif (size == 0): return "You roll " + str(num) + " pieces of air, and get air."
    elif (num > math.floor(5000/math.floor(math.log(size)))): doSanity = True 
    for _ in range(num):
        hold.append(random.randint(1, size))
    if doSanity: return "You roll " + str(num) + "d" + str(size) + ", and get: [i]" + str(sum(hold)) + "[/i]"
    else: return "You roll " + str(num) + "d" + str(size) + ", and get: [code]" + str(hold)[1:-1] + "[/code] (Total: [i]" + str(sum(hold)) + "[/i])"

def bot(bot_data, thread_data, user_data):
    output = "Bot Statistics:"
    output += "\n  Version: " + str(bot_data["version"])
    output += "\n  Uptime: " + str(datetime.datetime.now() - bot_data["uptime"])
    output += "\n  Parse Cycles: " + str(bot_data["data"]["parse_cycles"])
    output += "\n  Commands Found: " + str(bot_data["data"]["commands_found"])
    output += "\n  Commands Parsed: " + str(bot_data["data"]["commands_parsed"])
    output += "\n  Valid Commands: " + str(bot_data["data"]["valid_commands"])
    output += "\n  Threads Parsed: " + str(bot_data["thread_ids"])
    return output

def _help(bot_data, thread_data, user_data):
    output = "Commands:"
    output += "\n[quote]  nh!coin\n    Flips a coin and gives you the result.[/quote]"
    output += "\n[quote]  nh{dice|roll} num;int;1 sides;int;20\n    Rolls [i]num[/i] [i]sides[/i]-sided dice, and gives you the result.[/quote]"
    output += "\n[quote]  nh!bot\n    Returns various statistics about the bot.[/quote]"
    output += "\n[quote]  nh!help\n    Returns this help message.[/quote]"
    output += "\n[quote]  nh!suggest suggestion;str;allows_spaces\n   Make a suggestion.[/quote]"
    output += "\n[quote]  nh!threadInfo\n    Get information about the current thread.[/quote]"
    output += "\n[quote]  nh!text command;str;no_spaces;'read' filename;str;no_spaces;'_' other;varies\n    Text file modificaton.[/quote]"
    output += "\n[quote]  nh!{file|files} command;str;no_spaces;'read' filename;str;no_spaces;'_.txt' other;varies\n    File modificaton.[/quote]"
    output += "\n[quote]  nh!estimate tID;int;<current_thread>\n    Estimates when a thread will be completed.[/quote]"
    output += "\nArguments are in the form \"name;type;spaces;default\". Arguments with no default are required, [i]spaces[/i] is only present for strings."
    output += "\nFor more information (updated quicker), visit [url=https://realicraft.github.io/Nihonium/index.html]the webpage[/url]."
    return output

def suggest(bot_data, thread_data, user_data, *suggestion):
    if (len(suggestion) == 0): return "Your empty space has been recorded."
    suggestion_full = " ".join(suggestion)
    with open("suggestions.txt", "a", encoding="utf-8") as suggestFile:
        suggestFile.write(suggestion_full + "\n")
    return "Your suggestion has been recorded."

def threadInfo(bot_data, thread_data, user_data):
    adate = datetime.datetime(thread_data["date"]["year"], thread_data["date"]["month"], thread_data["date"]["day"], thread_data["date"]["hour"], thread_data["date"]["minute"], thread_data["date"]["second"])
    bdate = datetime.datetime.now()
    diff = bdate - adate
    ppd = thread_data["recentPost"] / (diff.days + (diff.seconds / 86400))
    output = "Thread Info:"
    output += "\n  Name: " + str(thread_data["name"])
    output += "\n  ID: " + str(thread_data["thread_id"])
    output += "\n  Types: " + str(thread_data["types"])
    output += "\n  Date: " + adate.strftime("%b %d, %Y %I:%M:%S %p")
    output += "\n  Posts/Day: ~" + str(round(ppd, 5))
    output += "\n  Posts/Hour: ~" + str(round(ppd/24, 5))
    if "goal" in thread_data: output += "\n  Goal: " + str(thread_data["goal"])
    if "postID" in thread_data["types"]:
        output += "\n  Completion: " + str(round((thread_data["recentPost"]/thread_data["goal"])*100, 2)) + "% (" + str(thread_data["recentPost"]) + "/" + str(thread_data["goal"]) + ")"
        until = thread_data["goal"] / ppd
        cdate = adate + datetime.timedelta(days=until)
        output += "\n  Est. Completion Date: " + cdate.strftime("%b %d, %Y %I:%M:%S %p")
    return output

def text(bot_data, thread_data, user_data, command="read", filename="_", *other):
    # commands:
    # read       | outputs the contents of the file
    # write      | replaces the contents of the file with " ".join(other)
    # append     | add " ".join(other) to the end of the file
    # appendline | add a new line at the end of the file, followed by " ".join(other)
    # insert     | insert " ".join(other[1:]) after character other[0]
    # cut        | cut a section of the file, removing it (clipboard will be emptied on paste)
    # copy       | copy a section of the file, trunciated if it ends outide the file
    # paste      | paste onto the end of the file, fails if the clipboard is empty
    # create     | create a file, fails if it exists
    # duplicate  | duplicate a file, fails if it does not exist
    # delete     | delete a file, fails if it does not exist
    # _.txt is unique in that append and insert behave like write, copy and cut select everything, paste overwrites everything, and create, duplicate, and delete all fail
    if filename == "_":
        if command == "append": command = "write"
        if command == "insert": command = "write"
    if command == "read":
        try:
            with open("files/" + filename + ".txt", "r", encoding="utf-8") as file: return "Contents of [i]" + filename + ".txt[/i]: \n" + file.read()
            logEntry("Read file '" + filename + ".txt'")
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "write":
        try:
            with open("files/" + filename + ".txt", "w+", encoding="utf-8") as file:
                file.write(" ".join(other))
                file.seek(0)
                logEntry("Wrote to file '" + filename + ".txt'")
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "append":
        try:
            with open("files/" + filename + ".txt", "a+", encoding="utf-8") as file:
                file.write(" ".join(other))
                file.seek(0)
                logEntry("Wrote to file '" + filename + ".txt'")
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "appendline":
        try:
            with open("files/" + filename + ".txt", "a+", encoding="utf-8") as file:
                file.write("\n")
                file.write(" ".join(other))
                file.seek(0)
                logEntry("Wrote to file '" + filename + ".txt'")
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "insert":
        try:
            with open("files/" + filename + ".txt", "r", encoding="utf-8") as file: temp = file.read()
            with open("files/" + filename + ".txt", "w+", encoding="utf-8") as file: file.write(temp[:other[0]] + " ".join(other[1:]) + temp[other[0]:])
            logEntry("Wrote to file '" + filename + ".txt'")
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "create":
        try:
            with open("files/" + filename + ".txt", "x", encoding="utf-8") as file: return "Successfully created [i]" + filename + ".txt[/i]"
            logEntry("Created file '" + filename + ".txt'")
        except IOError: return "A file by the name [i]" + filename + ".txt[/i] already exists."
    elif command == "duplicate":
        if filename == "_": return "Can't duplicate _."
        else:
            try:
                shutil.copy2("files/" + filename + ".txt", "files/copy_" + filename + ".txt")
                logEntry("Copied file '" + filename + ".txt' to 'copy_" + filename + ".txt'")
                return "Successfully duplicated [i]" + filename + ".txt[/i]"
            except FileNotFoundError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "delete":
        if filename == "_": return "Can't delete _."
        else:
            try:
                os.remove("files/" + filename + ".txt")
                logEntry("Deleted file '" + filename + ".txt'")
                return "Successfully deleted [i]" + filename + ".txt[/i]"
            except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    else: return "Invalid command: " + command

def files(bot_data, thread_data, user_data, command="read", filename="_.txt", *other):
    # commands:
    # read      | read the hex data of a file
    # rename    | rename a file
    # list      | list all files
    # move      | move a file
    # cut       | cut a section of the file, removing it (clipboard will be emptied on paste)
    # copy      | copy a section of the file, trunciated if it ends outide the file
    # paste     | paste onto the end of the file, fails if the clipboard is empty
    # create    | create a file, fails if it exists
    # duplicate | duplicate a file, fails if it does not exist
    # delete    | delete a file, fails if it does not exist
    if command == "read":
        try:
            with open("files/" + filename, "rb") as file:
                logEntry("Read file '" + filename + "'")
                output = "Contents of [i]" + filename + "[/i]: \n[code]"
                filehex = file.read().hex()
                filehexlist = []
                for i in range(0, len(filehex), 2):
                    filehexlist.append(filehex[i:i+2])
                d = "         x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 xA xB xC xD xE xF\n        ------------------------------------------------\n"
                for j in range(math.ceil(len(filehexlist)/16)):
                    d += "0x" + hex(j)[2:].rjust(3, "0") + "x |"
                    e = ""
                    for k in filehexlist[j*16:(j*16)+16]:
                        e += " " + k
                    d += e.ljust(48)
                    d += " | "
                    for l in filehexlist[j*16:(j*16)+16]:
                        if l == "0a": # newline
                            d += "↕"
                        elif l == "09": # tab
                            d += "↔"
                        elif l == "00": # null
                            d += "Φ"
                        elif int(l, 16) > 126: # outside ascii
                            d += "·"
                        elif int(l, 16) < 32: # before printable
                            d += "•"
                        elif l == "20": # space
                            d += "˽"
                        else: # other
                            m = bytes.fromhex(l)
                            d += m.decode("ASCII")
                    d += "\n"
                d = d[0:-1]
                output += d
                output += "[/code]"
                return output
        except IOError: return "No file by the name [i]" + filename + "[/i] exists."
    elif command == "rename":
        try:
            os.rename("files/" + filename, "files/" + other[0])
            logEntry("Renamed file '" + filename + "' to '" + other[0] + "'")
        except FileNotFoundError: return "No file by the name [i]" + filename + "[/i] exists."
        except FileExistsError: return "A file by the name [i]" + other[0] + "[/i] already exists."
    elif command == "list":
        output = "Files: [quote]"
        for i in os.listdir("files"):
            output += i + "\n"
        output += "[/quote]"
        return output
    elif command == "create":
        try:
            with open("files/" + filename, "x", encoding="utf-8") as file: return "Successfully created [i]" + filename + "[/i]"
            logEntry("Created file '" + filename + "'")
        except IOError: return "A file by the name [i]" + filename + "[/i] already exists."
    elif command == "duplicate":
        if filename == "_": return "Can't duplicate _."
        else:
            try:
                shutil.copy2("files/" + filename, "files/copy_" + filename)
                logEntry("Copied file '" + filename + "' to 'copy_" + filename + "'")
                return "Successfully duplicated [i]" + filename + "[/i]"
            except FileNotFoundError: return "No file by the name [i]" + filename + "[/i] exists."
    elif command == "delete":
        if filename == "_": return "Can't delete _."
        else:
            try:
                os.remove("files/" + filename)
                logEntry("Deleted file '" + filename + "'")
                return "Successfully deleted [i]" + filename + "[/i]"
            except IOError: return "No file by the name [i]" + filename + "[/i] exists."
    else: return "Invalid command: " + command

def estimate(bot_data, thread_data, user_data, tID=None):
    if tID is None:
        tID = thread_data["thread_id"]
    with open("threadData.json", "r+", encoding="utf-8") as threadfile:
        post_ids = json.loads(threadfile.read())
    thread_data2 = post_ids[str(tID)]
    adate = datetime.datetime(thread_data2["date"]["year"], thread_data2["date"]["month"], thread_data2["date"]["day"], thread_data2["date"]["hour"], thread_data2["date"]["minute"], thread_data2["date"]["second"])
    bdate = datetime.datetime.now()
    diff = bdate - adate
    ppd = thread_data2["recentPost"] / (diff.days + (diff.seconds / 86400))
    if "postID" in thread_data2["types"]:
        until = thread_data2["goal"] / ppd
        cdate = adate + datetime.timedelta(days=until)
        output = "Est. Completion Date: " + cdate.strftime("%b %d, %Y %I:%M:%S %p")
        if len(thread_data2["estimates"]) >= 1:
            output += "\nPrevious Estimates: [quote]"
            for i in thread_data2["estimates"]:
                output += "\n" + i
            output += "[/quote]"
        thread_data2["estimates"].append(cdate.strftime("%b %d, %Y %I:%M:%S %p"))
        with open("threadData.json", "w", encoding="utf-8") as l:
            l.write(json.dumps(post_ids, indent=4))
    else:
        output = "Unknown thread ID: [i]" + str(tID) + "[/i]"
    return output

def rollADice(bot_data, thread_data, user_data, action="roll"):
    with open("roll_a_dice.json", "r+", encoding="utf-8") as rollfile:
        roll_data = json.loads(rollfile.read())
    output = ""
    uID = str(user_data["uID"])
    if uID not in roll_data: roll_data[uID] = {"points": 0, "timer": 0}
    if action == "roll":
        roll_data2 = {**roll_data}
        del roll_data2["roll_last"]
        timenow = datetime.datetime.now(tz=datetime.timezone.utc)
        if roll_data[uID]["timer"] > timenow.timestamp(): return "You can't roll right now, you can roll again in about " + str(math.ceil((roll_data[uID]["timer"] - timenow.timestamp())/60)) + " minutes."
        done = False
        while not done:
            done = True
            result = random.randint(1, 10)
            output += "You rolled a " + str(result)
            if result == 1:
                roll_data[uID]["points"] += 1
                output += ", and gained one point."
            elif result == 2:
                roll_data[uID]["points"] += 2
                roll_data[uID]["timer"] = int((timenow + datetime.timedelta(hours=4)).timestamp())
                output += ", and gained two points. You can't roll for the next four hours."
            elif result == 3:
                hold = math.floor((int(timenow.timestamp()) - roll_data["roll_last"])/(60*60))
                roll_data[uID]["points"] += hold
                output += ", and gained " + str(hold) + " point" + ("s" if hold != 1 else "") + "."
            elif result == 4:
                hold = random.randint(1, 10)
                roll_data[random.choice(list(roll_data2.keys()))]["points"] -= hold
                output += ", causing someone random to lose " + str(hold) + " point" + ("s" if hold != 1 else "") + "."
            elif result == 5:
                hold = random.randint(1, 5)
                roll_data[random.choice(list(roll_data2.keys()))]["points"] -= hold
                roll_data[uID]["points"] += hold
                output += ", causing someone random to lose " + str(hold) + " point" + ("s" if hold != 1 else "") + ", and for you to recieve said lost points."
            elif result == 6:
                roll_data[uID]["points"] -= 1
                output += ", and lost one point."
            elif result == 7:
                roll_data[uID]["points"] += 1
                done = False
                output += ", gained one point, and get to roll again!\n"
            elif result == 8:
                roll_data[uID]["points"] += 1
                roll_data[random.choice(list(roll_data2.keys()))]["points"] += 2
                output += ", and gained one point, while someone random gained two."
            elif result == 9:
                hold = (random.randint(1, random.randint(1, 60)))
                roll_data[uID]["points"] += hold
                output += ", and gained points equal to how long you have on the 60 second rule.\n...we'll pretend that's " + str(hold) + "."
            elif result == 10:
                roll_data[uID]["points"] += 10
                roll_data[uID]["timer"] = int((timenow + datetime.timedelta(hours=12)).timestamp())
                output += ", and gained ten points! You can't roll for the next twelve hours, though."
        output += "\nYou now have " + str(roll_data[uID]["points"])+ " point" + ("s" if roll_data[uID]["points"] != 1 else "") + "."
        roll_data["roll_last"] = int(timenow.timestamp())
        with open("roll_a_dice.json", "w", encoding="utf-8") as rollfile:
            rollfile.write(json.dumps(roll_data, indent=4))
    elif action in ["points", "score", "check"]:
        hold = roll_data[uID]["points"]
        output += "You have " + str(hold) + " point" + ("s" if hold != 1 else "") + "."
    elif action in ["scoreboard", "leaderboard", "scores"]:
        output += "Current leaderboard:\n[quote]"
        roll_data2 = {**roll_data}
        del roll_data2["roll_last"]
        #based off of careerkarma.com/blog/python-sort-a-dictionary-by-value/
        for i in sorted(roll_data2, key=lambda x: roll_data[x]["points"]):
            output += str(i) + ": " + str(roll_data2[i]["points"]) + " point" + ("s" if roll_data2[i]["points"] != 1 else "") + "\n"
        output += "[/quote][i](Note: the leaderboard uses user IDs rather than usernames, as that is all that is stored.)[/i]"
    return output
#-------------------------
# Add commands above here.

# This registers the commands for use by Nihonium.
commands = {"coin": coin, "dice": dice, "roll": dice, "bot": bot, "help": _help, "suggest": suggest, "threadinfo": threadInfo, "text": text, "files": files, "file": files, "estimate": estimate, "rolladice": rollADice, "rolldice": rollADice}
# This registers commands exclusive to certain bots.
# Format: {"<id>": {"<command_name>": "<function>"}}
ex_commands = {"nihonium2": {"coin2": coin2}}