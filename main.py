"""A basic Discord intergration of Nihonium."""

import sys, math, random, os, json, datetime, traceback, re, requests # built-in modules
try: # custom modules
    import versions, commands 
    try: from commands import framework as fw
    except ImportError: pass
except ImportError:
    raise ImportError("Flerovium is missing some important files. Seek out setup.py to install it.")
import discord # the golden nugget

print("Flerovium: A basic Discord intergration of Nihonium.")

# Initialize variables
version = versions.Version(1, 1, 0)
bot_info = {"name": "Flerovium", "id": "flerovium", "prefix": "fl!"} # This identifies the bot running commands.py.
pattern = bot_info["prefix"]+"(.+)"                                  # This defines the command pattern.
fancy = "fancy" in sys.argv[1:]                                      # This enables fancy text. ($\alpha{}$)

# These variables are for debugging.
verbose = "verbose" in sys.argv[1:]                                  # This increases text output.
readOnly = "readonly" in sys.argv[1:]                                # This enables read-only mode.
legacy = "legacy" in sys.argv[1:]                                    # This enables full Nihonium-like behaviour.

jump = True
stats = {
"parse_cycles": None, 
"commands_parsed": 0, 
"commands_found": 0, 
"valid_commands": 0
}
uptime = datetime.datetime.now()

def ask(question, answers: dict, hideUI=False, printer=print, fancy=True):
    if not hideUI:
        printer(question)
        numLen = len(str(len(answers.keys())-1)) + 1
        if fancy:
            strLen = len(sorted(answers.keys(), key=lambda a: len(a), reverse=True)[0]) + 1
            print(f"┌{'─' * numLen}─┬─{'─' * strLen}┐")
            for a, x in enumerate(answers):
                print(f"│{str(a).rjust(numLen)} │ {x.ljust(strLen)}│")
            print(f"└{'─' * numLen}─┴─{'─' * strLen}┘")
        else:
            for a, x in enumerate(answers):
                print(f"{str(a).rjust(numLen)} : {x}")
    try: ans = int(input("> "))
    except: 
        print("Invalid input!")
        return ask(question, answers, hideUI=True)
    return answers[list(answers.keys())[ans]]

# Copied from Nihonium
def logEntry(entry: str, timestamp=None, printToScreen: bool=verbose):
    if timestamp is None: timestamp = datetime.datetime.now()
    if not readOnly:
        with open("logs/" + timestamp.strftime("%Y%m%d") + ".log", "a+", encoding="utf-8") as logfile:
            logfile.write("[" + timestamp.strftime("%I:%M:%S.%f %p") + "] " + entry + "\n")
            logfile.seek(0)
    if printToScreen: print(entry,file=sys.stderr)

def assemble_botdata():
    return {"uptime": uptime,
    "data": stats,
    "thread_ids": None,
    "post_ids": None,
    "cookies": None,
    "session": None,
    "headers": None,
    "version": version,
    "bot_info": bot_info, 
    }
    
def assemble_userdata(user):
    return {"name": user.name+"#"+user.discriminator,
    "uID": user.id}
    
logEntry("Using commands.py version "+str(commands.version if "version" in dir(commands) else commands.__version__))

# Get attributes
def getAttr():
    logEntry("Updating attribs.json...")
    with open("attribs.json", "wb") as f: f.write(requests.get("https://raw.githubusercontent.com/Gilbert189/Flerovium/main/attribs.json").content)
    logEntry("attribs.json updated.")
allowed = ["inc_commands", "replace", "attrs_version", "fancy", "readOnly", "verbose", "legacy", "pattern"]
important = ["bot_info"]

getAttr()
with open("attribs.json", "r+") as f: 
    for x, i in json.loads(f.read()).items():
        if x in allowed: globals()[x] = i
        elif x in important: 
            if ask("An attempt to modify the variable {} has been detected.\nThis variable is important for Flerovium, and changing it may alter its behavour.\nWhat will you do?",{"Modify the variable":True,"Keep it unchanged":False}):
                globals()[x] = i
if attrs_version in globals(): logEntry("Using ext. attributes v%d"%attrs_version)
if legacy: logEntry("Flerovium is in legacy mode. Features like posting Discord embeds will be disabled.",printToScreen=True)
if readOnly: logEntry("Flerovium is in read-only mode. Logs and statistics will freeze or simply not work.",printToScreen=True)

# Statistics stuff
def saveStats():
    global stats
    with open("data.json","w",encoding="utf-8") as data:
        data.write(json.dumps(stats))
        
def loadStats():
    global stats
    try:
        with open("data.json","r",encoding="utf-8") as data:stats = json.loads(data.read())
    except IOError: 
        logEntry("data.json not found, making one instead")
        saveStats()    
        
def showStats():
    global stats, jump, fancy, verbose
    if verbose:
        logEntry("Found {} posts, parsed {} commands, {} of them is valid".format(stats["commands_found"],stats["commands_parsed"],stats["valid_commands"]))
    else:
        output = "Flerovium is active.\n\n" if fancy else ""
        if fancy:
            # i forgot where did i find this
            os.system('cls' if os.name == 'nt' else 'clear')
        else: output += "\r\x1B[2F" if jump else ""
        output += "Posts found:     "+str(stats["commands_found"])
        output += "\nCommands parsed: "+str(stats["commands_parsed"])
        output += "\nValid commands:  "+str(stats["valid_commands"])
        jump = True
        if fancy:
            output += "\n\n\nSystem messages:\n"
        print(output,end="")
loadStats()

# Get token
try:
    with open("token.txt", "r+") as f: token = f.read()
except IOError: raise IOError("token.txt not found") from None

# Check compatibility with Flerovium
if bot_info["id"] not in commands.alt_minvers:
    logEntry("The copy of commands.py doesn't have alt_minvers argument set.")
    ask("The copy of commands.py doesn't have Flerovium on alt_minvers.\nWe don't know if this copy supports Flerovium.\nContinue anyway?",{"Yes":lambda:0,"No":exit})()
elif commands.alt_minvers[bot_info["id"]] > version:
    raise ImportError(
        "The copy of commands.py is incompatible with this version of Flerovium."+
        "\nFlerovium is in version {}, while commands.py requires at least {}".format(str(version),str(commands.flerovium_minver))
    )
            
# A function to convert TBG formatting tags to Discord formatting tags
def formatToDiscord(text):
    replace = {
        "b":"**",
        "i":"_",
        "u":"__",
        "s":"~~",
        "code":"\n```\n",
        "quote":"\n```\n"
    }
    for t,d in replace.items():text = re.sub("\[{}(?:=.+?)?\]|\[/{}\]".format(t, t), d, text)
    return text

# the bot
class Flerovium(discord.Client):
    async def on_ready(self):
        logEntry('Logged on as '+str(self.user),printToScreen=True)
        print("Flerovium is active."+("\n\n" if not verbose else ""))
        showStats()
        
    # client.change_presence(activity=game)

    async def on_message(self, message):
        def getFunction(match):
            match[0] = match[0].lower()
            if "ex_commands" in dir(commands):
                if "flerovium" in commands.ex_commands:
                    if match[0] in commands.ex_commands["flerovium"]:
                        funct = commands.ex_commands["flerovium"][match[0]]
                        if "Command" in type(funct).__name__: funct = funct.command
                        return funct
            if match[0] in commands.commands:
                funct = commands.commands[match[0]]
                if "Command" in type(funct).__name__: funct = funct.command
                if funct.__name__ in inc_commands:
                    return lambda *a: ":no_entry_sign: The command you issued is incompatible with Flerovium."
                else: 
                    return funct
            
        saveStats()
        phase = "parsing"
        try:
            # don't respond to ourselves
            if message.author == self.user:
                return
            stats["commands_found"]+=1
            showStats()
            logEntry("Received message {} from {}".format(message.content,message.author))
            
            # parse the message
            match = re.search(pattern,message.content)
            if match: match = match.group(1)
            else: return
            match = match.split(" ")
            stats["commands_parsed"]+=1
            showStats()
            
            # interpret the command
            phase = 'interpreting'
            output = None
            func = getFunction(match)
            if not output:
                if len(match) > 1: output=func(assemble_botdata(),{},assemble_userdata(message.author),*match[1:])
                elif func: output=func(assemble_botdata(),assemble_userdata(message.author),{})
                else: output=":no_entry_sign: Flerovium cannot process your command. (yet)"
            
            # send the post
            if type(output)==discord.Embed: await message.channel.send(embed=output)
            elif type(output)==str: 
                # replace the text
                for x, rep in replace.items():
                    if "__name__" in dir(func):
                        if x == func.__name__:
                            for fr, to in rep.items(): output = re.sub(fr, to, output)
                output = formatToDiscord(output)
                await message.channel.send(output)
            else: await message.channel.send(output)
            
            logEntry("Sent "+ repr(output))
            stats["valid_commands"]+=1
            showStats()
        except (TypeError, ValueError, KeyError, IndexError, OverflowError, ZeroDivisionError) as e:
            tb = traceback.format_exc()
            await message.channel.send('While {phase} that command, an error occured:\n```\n{tb}\n```'.format(**{**locals(),**globals()}))
            logEntry("{} while {} command {}: {}".format(type(e).__name__,phase,repr(message),e),fancy)
            jump = False 
            if verbose: raise
        
client = Flerovium()
print("Logging in...")
client.run(token)
