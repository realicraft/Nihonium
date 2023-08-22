import versions
from . import framework as fw # These imports are required. (The "as fw" is not required, and is only here to shorten lines.)
import random, math, datetime, json # These imports are dependent on what your commands need.

# This file can be used as an example of a command file.

version = versions.Version(1, 9, 1)                     # This defines the version of the user-added commands.
nihonium_minver = versions.Version(0, 13, 0)            # This defines the minimum version of Nihonium needed to run these commands.
alt_minvers = {"nihonium2": versions.Version(0, 13, 0)} # Used to define minimum versions for other bots. Format: {"<id>": versions.Version(<version>)}

# Commands can take any number of placement arguments and should return a string containing the output of the command. (Beginning/trailing newline not required.)
# Commands can take inputs that are Integers, Floats, Strings, and Booleans. 
# If a command raises TypeError, ValueError, KeyError, IndexError, OverflowError, or ZeroDivisionError, it will be caught by Nihonium. Other errors will not be caught.
# The first argument a command recieves will contain information about the bot.
# The second argument a command recieves will contain information about the thread the command was called in.
# The third argument a command recieves will contain information about the user who called the command.

# The functions below are executed when certain commands are called:
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
    elif (num*size >= 1000000000): return "That's [i]way[/i] too many for me to roll." # avoid MemoryError
    elif (num > math.floor(5000/math.floor(math.log(size)))): doSanity = True 
    for _ in range(num):
        hold.append(random.randint(1, size))
    if doSanity: return "You roll " + str(num) + "d" + str(size) + ", and get: [i]" + str(sum(hold)) + "[/i]"
    else: return "You roll " + str(num) + "d" + str(size) + ", and get: [code]" + str(hold)[1:-1] + "[/code] (Total: [i]" + str(sum(hold)) + "[/i])"

def bot(bot_data, thread_data, user_data):
    output = "Bot Statistics:"
    output += "\n  Nihonium Version: " + str(bot_data["version"])
    output += "\n  Fork Version: " + str(bot_data["forkversion"])
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
    output += "\n[quote]  nh!{dice|roll} num;int;1 sides;int;20\n    Rolls [i]num[/i] [i]sides[/i]-sided dice, and gives you the result.[/quote]"
    output += "\n[quote]  nh!bot\n    Returns various statistics about the bot.[/quote]"
    output += "\n[quote]  nh!help\n    Returns this help message.[/quote]"
    output += "\n[quote]  nh!suggest suggestion;str;allows_spaces\n    Make a suggestion.[/quote]"
    output += "\n[quote]  nh!threadInfo\n    Get information about the current thread.[/quote]"
    output += "\n[quote]  nh!text command;str;no_spaces;'read' filename;str;no_spaces;'_' other;varies\n    Text file modificaton.[/quote]"
    output += "\n[quote]  nh!{file|files} command;str;no_spaces;'read' filename;str;no_spaces;'_.txt' other;varies\n    File modificaton.[/quote]"
    output += "\n[quote]  nh!estimate tID;int;<current_thread>\n    Estimates when a thread will be completed.[/quote]"
    output += "\n[quote]  nh!choose options;multi_str;no_spaces\n    Picks one of the given options.[/quote]"
    output += "\n[quote]  nh!estimate action;str;no_spaces;'roll'\n    Used for [topic=5893]TGOHNRADFYASWH[/topic].[/quote]"
    output += "\nArguments are in the form \"name;type;spaces;default\". Arguments with no default are required, [i]spaces[/i] is only present for strings."
    output += "\nFor more information (updated quicker), visit [url=https://realicraft.github.io/Nihonium/index.html]the webpage[/url]."
    output += "\n(Note: I plan on adding a system to auto-generate the results of this command. It hasn't been added yet, though.)"
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

def estimate(bot_data, thread_data, user_data, tID=None):
    # fix allowing you to estimate non-tracked threads
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
            output += "\nPrevious Estimates: [code]"
            for i in thread_data2["estimates"]:
                output += "\n(" + i[0] + ") " + i[1]
            output += "[/code]"
        thread_data2["estimates"].append([bdate.strftime("%b %d, %Y %I:%M:%S %p"), cdate.strftime("%b %d, %Y %I:%M:%S %p")])
        with open("threadData.json", "w", encoding="utf-8") as l:
            l.write(json.dumps(post_ids, indent=4))
    else:
        output = "Unknown thread ID: [i]" + str(tID) + "[/i]"
    return output

def choose(bot_data, thread_data, user_data, *options):
    if (len(options) == 0):
        return "You didn't give anything for me to choose."
    else:
        return random.choice(["I'll go with ", "How about...", "Rolled a 1d"+str(len(options))+", and got ", "Picked randomly, and got ", "The bot chooses ", "Let's go with ", "That one, the one that says "]) + "\"" + random.choice(options) + "\"."

# These turn the functions above into commands:
coinCommand = fw.Command("coin", coin, [], helpShort="Flips a coin and gives you the result.", helpLong="Flips a coin and gives you the result.")
diceCommand = fw.Command("dice", dice,
                        [fw.CommandInput("num", "int", "1", "The number of dice."), fw.CommandInput("size", "int", "20", "The number of sides on the dice.")],
                        helpShort="Rolls [i]num[/i] [i]sides[/i]-sided dice, and gives you the result.",
                        helpLong="Rolls [i]num[/i] [i]sides[/i]-sided dice, and gives you the result.")
botCommand = fw.Command("bot", bot, [], helpShort="Returns various statistics about the bot.", helpLong="Returns various statistics about the bot.")
helpCommand = fw.Command("help", _help, [])
suggestCommand = fw.Command("suggest", suggest, [fw.CommandInput("suggestion", "str")])
tiCommand = fw.Command("threadInfo", threadInfo, [])
estiCommand = fw.Command("estimate", estimate, [fw.CommandInput("tID", "int", "<current_thread>")])
chooseCommand = fw.Command("choose", choose, [fw.CommandInput("options", "multi_str")])

# This registers the commands for use by Nihonium.
commandlist = {"coin": coinCommand, "dice": diceCommand, "roll": diceCommand, "bot": botCommand, "botinfo": botCommand, "help": helpCommand, "suggest": suggestCommand, "threadinfo": tiCommand, "estimate": estiCommand, "choose": chooseCommand, "choise": chooseCommand}
# This registers commands exclusive to certain bots.
# Format: {"<id>": {"<command_name>": "<function>"}}
ex_commandlist = {"nihonium2": {"coin2": coin2}}
# This registers functions to be performed at the end of a parse-cycle.
do_last = []
# This registers functions to be performed at the beginning of a parse-cycle.
do_first = []