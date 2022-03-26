# This file provides some framework for commands, including a class for commands.
import typing

class CommandInput:
    """A class for implementing command inputs."""
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
    """A class for implementing commands."""
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
