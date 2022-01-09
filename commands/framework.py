# This file provides some framwork for commands, including a class for commands.
# It also provides access to the logEntry() function.
import typing, datetime

# from main.py
def logEntry(entry: str, timestamp=None):
    if timestamp is None: timestamp = datetime.datetime.now()
    with open("logs/" + timestamp.strftime("%Y%m%d") + ".log", "a+", encoding="utf-8") as logfile:
        logfile.write("[" + timestamp.strftime("%I:%M:%S.%f %p") + "] " + entry + "\n")
        #logfile.seek(0)
        #line_count = 0
        #for _ in logfile: line_count += 1
        #writeText(97, 2, str(line_count).rjust(4) + " entries in log file", 0, 7)

class CommandInput:
    """A class for implementing commands inputs."""
    def __init__(self, name: str, _type: str, default: str="", desc: str=""):
        self.name = name
        self.type = _type
        self.default = default
        self.desc = desc
        self.hasdefault = (False if self.default == "" else True)
        self.hasdesc = (False if self.desc == "" else True)
    
    def getShort(self) -> str:
        return self.name + ";" + self.type + (";" + self.default if self.hasdefault else "")
    
    def getLong(self) -> str:
        return "(" + self.type + ") " + self.name + (" " + self.desc if self.hasdesc else "") + (" (Defaults to " + self.default + ")" if self.hasdefault else "")

class Command:
    """A class for implimenting commands."""
    def __init__(self, name: str, command: typing.Callable[..., str], inputs: typing.List[CommandInput], *, helpShort: str="", helpLong: str=""):
        self.name = name
        self.command = command
        self.inputs = inputs
        self.help = {"s": helpShort, "l": helpLong}
        self.hashelp = {"s": (False if self.help["s"] == "" else True), "l": (False if self.help["l"] == "" else True)}
    
    def run(self, *args, **kwargs) -> str:
        """Alternative for calling `Command.command` directly."""
        return self.command(*args, **kwargs)
    
    def getShortHelp(self, prefix: str) -> str:
        hold = "[quote] " + prefix + self.name
        if len(self.inputs) != 0:
            for i in self.inputs:
                hold += " " + i.getShort()
        hold += "\n    "
        hold += (self.help["s"] if self.hashelp["s"] else "No short help was specified for this command.")
        hold += "[/quote]"
        return hold
    
    def getLongHelp(self, prefix: str) -> str:
        hold = "[quote] " + prefix + self.name + "\n"
        if len(self.inputs) != 0:
            for i in self.inputs:
                hold += "    " + i.getLong() + "\n"
        hold += (self.help["l"] if self.hashelp["l"] else "No long help was specified for this command.")
        hold += "[/quote]"
        return hold