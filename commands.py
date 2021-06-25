import random, math, datetime, time, sys, os, versions
from lxml import html

# This file is used to define the commands used by Nihonium.

__version__ = versions.Version(1, 1)        # This defines the version of the modules framework.
version = versions.Version(1, 6, 0)         # This defines the version of the user-added commands.
nihonium_minver = versions.Version(0, 5, 2) # This defines the minimum version of Nihonium needed to run these commands.

# Commands can take any number of placement arguments and should return a string containing the output of the command. (Beginning/Trailing newline not required.)
# Commands can take inputs that are Integers, Floats, Strings, and Booleans. 
# If a command raises TypeError, ValueError, KeyError, IndexError, OverflowError, or ZeroDivisionError, it will be caught by Nihonium. Other errors will not be caught.
# The first argument a command recieves will contain information about the bot.
# The second argument a command recieves will contain information about the thread the command was called in.

# Add commands below here.
#-------------------------
def coin(bot_data, thread_data):
    return "You flip a coin, and get " + random.choice(["heads", "tails"]) + "."

def dice(bot_data, thread_data, num=1, size=20):
    num = int(float(num))
    size = int(float(size))
    hold = []
    if (num < 0): return "You can't roll negative dice."
    elif (num == 0): return "You roll no dice, and get nothing."
    elif (size < 0): return "You can't roll something that doesn't exist."
    elif (size == 0): return "You roll " + str(num) + " pieces of air, and get air."
    for i in range(num):
        hold.append(random.randint(1, size))
    return "You roll " + str(num) + "d" + str(size) + ", and get: [code]" + str(hold)[1:-1] + "[/code]"

def bot(bot_data, thread_data):
    output = "Bot Statistics:\n  Uptime: " + str(datetime.datetime.now() - bot_data["uptime"])
    output += "\n  Parse Cycles: " + str(bot_data["data"]["parse_cycles"])
    output += "\n  Commands Found: " + str(bot_data["data"]["commands_found"])
    output += "\n  Commands Parsed: " + str(bot_data["data"]["commands_parsed"])
    output += "\n  Valid Commands: " + str(bot_data["data"]["valid_commands"])
    output += "\n  Threads Parsed: " + str(bot_data["thread_ids"])
    return output

def _help(bot_data, thread_data):
    output = "Commands:"
    output += "\n[quote]  nh!coin\n    Flips a coin and gives you the result.[/quote]"
    output += "\n[quote]  nh{dice|roll} num;int;1 sides;int;20\n    Rolls [i]num[/i] [i]sides[/i]-sided dice, and gives you the result.[/quote]"
    output += "\n[quote]  nh!bot\n    Returns various statistics about the bot.[/quote]"
    output += "\n[quote]  nh!help\n    Returns this help message.[/quote]"
    output += "\nArguments are in the form \"name;type;default\". Arguments with no default are required."
    output += "\nFor more information (updated quicker), visit [url=https://realicraft.github.io/nihonium/index.html]the webpage[/url]."
    return output

def suggest(bot_data, thread_data, *suggestion):
    if (len(suggestion) == 0): return "Your empty space has been recorded."
    suggestion_full = " ".join(suggestion)
    i = 0
    while i < len(suggestion_full):
        if suggestion_full[i] == "&":
            if suggestion_full[i:i+4] == "&lt;": suggestion_full = suggestion_full[:i] + "<" + suggestion_full[i+4:]
            if suggestion_full[i:i+4] == "&gt;": suggestion_full = suggestion_full[:i] + ">" + suggestion_full[i+4:]
            if suggestion_full[i:i+5] == "&amp;": suggestion_full = suggestion_full[:i] + "&" + suggestion_full[i+5:]
        i += 1
    with open("suggestions.txt", "a") as suggestFile:
        suggestFile.write(suggestion_full + "\n")
    return "Your suggestion has been recorded."

def threadInfo(bot_data, thread_data):
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
    if "goal" in thread_data:
        output += "\n  Goal: " + str(thread_data["goal"])
    if "postID" in thread_data["types"]:
        output += "\n  Completion: " + str(round((thread_data["recentPost"]/thread_data["goal"])*100, 2)) + "% (" + str(thread_data["recentPost"]) + "/" + str(thread_data["goal"]) + ")"
        until = thread_data["goal"] / ppd
        cdate = adate + datetime.timedelta(days=until)
        output += "\n  Est. Completion Date: " + cdate.strftime("%b %d, %Y %I:%M:%S %p")
    return output

def text(bot_data, thread_data, filename="_", command="read", *other):
    # commands:
    # read   | outputs the contents of the file
    # write  | replaces the contents of the file with " ".join(other)
    # append | add a new line the the end of the file, followed by " ".join(other)
    # insert | insert " ".join(other[1:]) after character other[0]
    # create | create a file, fails if it exists
    # delete | delete a file, fails if it does not exist
    # _.txt is unique in that append and insert behave like write, and create and delete both fail
    if filename == "_":
        if command == "append": command = "write"
        if command == "insert": command = "write"
    if command == "read":
        try:
            with open("files/" + filename + ".txt", "r") as file:
                return "Contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError:
            return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "write":
        try:
            with open("files/" + filename + ".txt", "w+") as file:
                file.write(" ".join(other))
                file.seek(0)
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError:
            return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "append":
        try:
            with open("files/" + filename + ".txt", "a+") as file:
                file.write(" ".join(other))
                file.seek(0)
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError:
            return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "insert":
        try:
            with open("files/" + filename + ".txt", "r") as file:
                temp = file.read()
            with open("files/" + filename + ".txt", "w+") as file:
                file.write(temp[:other[0]] + " ".join(other[1:]) + temp[other[0]:])
        except IOError:
            return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "create":
        try:
            with open("files/" + filename + ".txt", "x") as file:
                return "Successfully created [i]" + filename + ".txt[/i]"
        except IOError:
            return "A file by the name [i]" + filename + ".txt[/i] already exists."
    else:
        return "Invalid command: " + command
#-------------------------
# Add commands above here.

# This registers the commands for use by Nihonium.
commands = {"coin": coin, "dice": dice, "roll": dice, "bot": bot, "help": _help, "suggest": suggest, "threadInfo": threadInfo, "threadinfo": threadInfo, "text": text}