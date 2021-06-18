import random, math, datetime, time, sys, os, versions
from lxml import html

# This file is used to define the commands used by Nihonium.

__version__ = versions.Version(1, 0)
nihonium_minver = versions.Version(0, 3, 5) # This defines the minimum version of Nihonium needed to run these commands.

# Commands can take any number of placement arguments and should return a string containing the output of the command. (Beginning/Trailing newline not required.)
# Commands can take inputs that are Integers, Floats, Strings, and Booleans. 
# If a command raises TypeError, ValueError, KeyError, IndexError, OverflowError, or ZeroDivisionError, it will be caught by Nihonium. Other errors will not be caught.
# The first argument a command recieves will contain information about the bot.

# Add commands below here.
#-------------------------
def coin(bot_data):
    return "You flip a coin, and get " + random.choice(["heads", "tails"]) + "."

def dice(bot_data, num: int=1, size: int=20):
    hold = []
    for i in range(num):
        hold.append(random.randint(1, size))
    return "You roll " + str(num) + "d" + str(size) + ", and get: [code]" + str(hold)[1:-1] + "[/code]"

def bot(bot_data):
    output += "\nBot Statistics:\n  Uptime: " + str(datetime.datetime.now() - bot_data["uptime"])
    output += "\n  Parse Cycles: " + str(bot_data["data"]["parse_cycles"])
    output += "\n  Commands Found: " + str(bot_data["data"]["commands_found"])
    output += "\n  Commands Parsed: " + str(bot_data["data"]["commands_parsed"])
    output += "\n  Valid Commands: " + str(bot_data["data"]["valid_commands"])
    output += "\n  Threads Parsed: " + str(bot_data["thread_ids"])
#-------------------------
# Add commands above here.

# This registers the commands for use by Nihonium.

commands = {"coin": coin, "dice": dice, "roll": dice, "bot": bot}