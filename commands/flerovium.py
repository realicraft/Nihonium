import versions, datetime
from . import framework as fw

version = versions.Version(1, 7, 5)                     # This defines the version of the user-added commands.
nihonium_minver = versions.Version(0, 10, 0)            # This defines the minimum version of Nihonium needed to run these commands.
alt_minvers = {"flerovium": versions.Version(1, 1, 0)} # Used to define minimum versions for other bots. Format: {"<id>": versions.Version(<version>)}

def bot(bot_data, thread_data, user_data):
    import discord
    output = discord.Embed(title="Bot Statistics")
    output.add_field(name="Version", value=str(bot_data["version"]))
    output.add_field(name="Uptime", value=str(datetime.datetime.now() - bot_data["uptime"]))
    output.add_field(name="Commands Found", value=str(bot_data["data"]["commands_found"]))
    output.add_field(name="Commands Parsed", value=str(bot_data["data"]["commands_parsed"]))
    output.add_field(name="Valid Commands", value=str(bot_data["data"]["valid_commands"]))
    return output

def help(bot_data, thread_data, user_data):
    import discord
    output = discord.Embed(title="Commands")
    output.add_field(name="fl!coin",value="Flips a coin and gives you the result.")
    output.add_field(name="nh{dice|roll} num;int;1 sides;int;20",value="Rolls *num* *sides*-sided dice, and gives you the result.")
    output.add_field(name="fl!bot",value="Returns various statistics about the bot.")
    output.add_field(name="fl!help",value="Returns this help message.")
    output.add_field(name="fl!suggest suggestion;str;allows_spaces",value="Make a suggestion.")
    output.add_field(name="fl!text command;str;no_spaces;'read' filename;str;no_spaces;'_' other;varies",value="Text file modificaton.")
    output.add_field(name="fl!{file|files} command;str;no_spaces;'read' filename;str;no_spaces;'_.txt' other;varies",value="File modificaton.")
    footer = "Arguments are in the form \"name;type;default\". Arguments with no default are required."
    footer += "\nFor more information about commands (updated quicker), visit https://realicraft.github.io/nihonium/index.html."
    footer += "\nFor more information about Flerovium, visit [link later]"
    output.add_field(name="Info",value=footer)
    return output
    
botCommand = fw.Command("bot", bot, [], helpShort="Returns various statistics about the bot.",
                                        helpLong="Returns various statistics about the bot.")
helpCommand = fw.Command("help", help, [])

commandlist = {}
ex_commandlist = {"flerovium": {"bot": botCommand, "help": helpCommand}}