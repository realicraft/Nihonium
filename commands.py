import random, math, datetime, time, sys, os, versions
from lxml import html

# This file is used to define the commands used by Nihonium.

__version__ = versions.Version(1, 1)        # This defines the version of the modules framework.
version = versions.Version(1, 4)            # This defines the version of the user-added commands.
nihonium_minver = versions.Version(0, 5, 0) # This defines the minimum version of Nihonium needed to run these commands.

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
    num = int(num)
    size = int(size)
    hold = []
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
    suggestion_full = " ".join(suggestion)
    with open("suggestions.txt", "a") as suggestFile:
        suggestFile.write(suggestion_full + "\n")
    return "Your suggestion has been recorded."

def threadInfo(bot_data, thread_data):
    output = "Thread Info:"
    output += "\n  Name: " + str(thread_data["name"])
    output += "\n  ID: " + str(thread_data["thread_id"])
    output += "\n  Types: " + str(thread_data["types"])
    if "goal" in thread_data:
        output += "\n  Goal: " + str(thread_data["goal"])
        output += "\n  Completion: " + str(round((thread_data["recentPost"]/thread_data["goal"])*100, 2)) + "% (" + str(thread_data["recentPost"]) + "/" + str(thread_data["goal"]) + ")"
    return output
#-------------------------
# Add commands above here.

# This registers the commands for use by Nihonium.

commands = {"coin": coin, "dice": dice, "roll": dice, "bot": bot, "help": _help, "suggest": suggest, "threadInfo": threadInfo}