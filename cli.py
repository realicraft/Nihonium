"""
A (not human-friendly) CLI for Flerovium.
Does double duty as a bridge to Java.
"""
import sys, json, commands, versions, re, datetime, getopt

# Initialize variables 
version = versions.Version(2, 0, 0)         # Specifies this CLI version.

with open("config.json", "r") as f:
    config = json.loads(f.read())
    for k, v in config.items(): globals()[k] = v

uptime = datetime.datetime.fromisoformat(uptime)

pattern = bot_info["prefix"]+"(.+)"

# Copied from Nickel
def logEntry(entry: str, timestamp=None, printToScreen: bool=verbose, severity=0):
    if timestamp is None: timestamp = datetime.datetime.now()
    if not readOnly:
        if not os.path.isdir('logs'): os.mkdir('logs')
        with open("logs/" + timestamp.strftime("%Y%m%d") + ".log", "a+", encoding="utf-8") as logfile:
            logfile.write(f"[{timestamp.strftime('%I:%M:%S.%f %p')} {['INFO','WARNING','ERROR'][severity]}] " + entry + "\n")
            logfile.seek(0)
    if printToScreen: 
        if severity==0: print(entry,file=sys.stderr)
        elif severity==1: warnings.warn(entry)
        elif severity==2: raise RuntimeException(entry)

def assemble_botdata():
    return {
        "uptime": uptime,
        "data": stats,
        "thread_ids": None,
        "post_ids": None,
        "cookies": None,
        "session": None,
        "headers": None,
        "version": version,
        "bot_info": bot_info
    }
    
def assemble_userdata(user):
    return {
        "name": f"{user}#{discriminator}",
        "uID": uid
    }

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

# Get attributes
def getAttr():
    #logEntry("Updating attribs.json...")
    #with open("attribs.json", "wb") as f: f.write(requests.get("https://raw.githubusercontent.com/Gilbert189/Flerovium/main/attribs.json").content)
    logEntry("attribs.json updated.")
allowed = ["inc_commands", "replace", "attrs_version", "fancy", "readOnly", "verbose", "legacy", "pattern"]
important = ["bot_info"]

with open("attribs.json", "r+") as f: 
    for x, i in json.loads(f.read()).items():
        if x in allowed: globals()[x] = i

# Check compatibility with Flerovium
if bot_info["id"] not in commands.alt_minvers:
    logEntry("The copy of commands.py doesn't have alt_minvers argument set.", severity=1)
    #ask("The copy of commands.py doesn't have Flerovium on alt_minvers.\nWe don't know if this copy supports Flerovium.\nContinue anyway?",{"Yes":lambda:0,"No":exit})()
elif commands.alt_minvers[bot_info["id"]] > version:
    raise ImportError(
        "The copy of commands.py is incompatible with this version of Flerovium."+
        "\nFlerovium is in version {}, while commands.py requires at least {}".format(str(version),str(commands.flerovium_minver))
    )

def formatToDiscord(text):
    """A function to convert TBG formatting tags to Discord formatting tags."""
    replace = {
        "b":"**",
        "i":"_",
        "u":"__",
        "s":"~~",
        "code":"\n```\n",
        "quote":"\n```\n"
        "url":f"({a.group(1)})" if len(a.groups) > 0 else ""
    }
    for t,d in replace.items():text = re.sub(r"\[{}(=.+?)?\]|\[/{}\]".format(t, t), d, text)
    return text

logEntry(f"Received {sys.argv}")

user, discriminator, uid = sys.argv[1:4]
discriminator = int(discriminator)

args = sys.argv[4:]

output = None
func = getFunction(args)
if not output:
    if len(args) > 1: output=func(assemble_botdata(),{},assemble_userdata(user),*args[1:])
    elif func: output=func(assemble_botdata(),assemble_userdata(user),{})
    else: output=":no_entry_sign: Flerovium cannot process your command. (yet)"
    
if type(output)==str: 
    # replace the text
    for x, rep in replace.items():
        if "__name__" in dir(func):
            if x == func.__name__:
                for fr, to in rep.items(): output = re.sub(fr, to, output)
    output = formatToDiscord(output)
    output = {"type": "text", "data": output}

print(json.dumps(output))
    
