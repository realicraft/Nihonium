"""A basic Discord intergration of Nihonium."""

import sys, math, random, os, json, datetime, traceback, re # built-in modules
import versions, commands # custom modules
import discord # the golden nugget

# Initialize variables
version = versions.Version(0, 1, 1)
bot_info = {"name": "Flerovium", "id": "flerovium", "prefix": "fl!"} # This identifies the bot running commands.py.
pattern = bot_info["prefix"]+"(.+)"                                  # This defines the command pattern.
legacy = False                                                       # This enables full Nihonium-like behaviour.
inc_commands = (commands.estimate, commands.threadInfo)              # This lists commands that are not supported by Flerovium.

jump = True
stats = {
"parse_cycles": None, 
"commands_parsed": 0, 
"commands_found": 0, 
"valid_commands": 0
}
uptime = datetime.datetime.now()

# Copied from Nihonium
def logEntry(entry: str, timestamp=None, printToScreen: bool=False):
	if timestamp is None: timestamp = datetime.datetime.now()
	with open("logs/" + timestamp.strftime("%Y%m%d") + ".log", "a+", encoding="utf-8") as logfile:
		logfile.write("[" + timestamp.strftime("%I:%M:%S.%f %p") + "] " + entry + "\n")
		logfile.seek(0)
		line_count = 0
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
	"is_flerovium": not legacy # for compatibility with commands.py 0.8.0-fl
	}
	
logEntry("Using commands.py version "+str(commands.version))
if legacy: logEntry("Legacy mode is on.",printToScreen=True)

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
	global stats, jump
	output  = "\r\x1B[2F" if jump else ""
	output += "Posts found:     "+str(stats["commands_found"])
	output+="\nCommands parsed: "+str(stats["commands_parsed"])
	output+="\nValid commands:  "+str(stats["valid_commands"])
	jump = True
	print(output,end="")
loadStats()

# Get token
try:
	with open("token.txt", "r+") as f: token = f.read()
except IOError: raise IOError("token.txt not found") from None

# Enhanced attributes! (Check compatibility with Flerovium)
ext_attrs = ['flerovium_commands','flerovium_inc_commands']
if not all(x in dir(commands) for x in ext_attrs):
	for x in filter(lambda a: a not in ext_attrs, dir(commands)):
		logEntry("The copy of commands.py doesn't have {x} set. Please check if the copy is compatible.".format({**locals(),**globals()}),printToScreen=True)
if "flerovium_compatible" in dir(commands):
	if not commands.flerovium_compatible:
		raise ImportError("The copy of commands.py is not Flerovium compatible.") from None
if "flerovium_minver" in dir(commands):
		if commands.flerovium_minver > version:
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
		"code":"```"
	}
	for t,d in replace.items():text = re.sub("\[{}(?:=.+?)?\]|\[/{}\]".format(t, t), d, text)
	return text

# the bot
class Flerovium(discord.Client):
	async def on_ready(self):
		logEntry('Logged on as '+str(self.user),printToScreen=True)
		print("Flerovium is active.\n\n")
		showStats()

	async def on_message(self, message):
		def getFunction(match):
			if "exc_commands" in dir(commands):
				logEntry("exc_commands is in commands")
				if bot_info["id"] in commands.exc_commands: 
					logEntry("id is in exc_commands")
					if match[0] in commands.exc_commands["flerovium"]:
						logEntry("Found in exc_commands")
						return commands.exc_commands["flerovium"]
			if "flerovium_commands" in dir(commands):
				logEntry("flerovium_commands is in commands")
				# legacy support
				if match[0] in commands.flerovium_commands and not legacy:
					# use Flerovium-exclusive commands
					logEntry("Found in flerovium_commands")
					return commands.flerovium_commands[match[0]]
			if match[0] in commands.commands:
				logEntry("Found in commands, unknown compatibility")
				# legacy support
				if "flerovium_inc_commands" in dir(commands):
					logEntry("flerovium_inc_commands is in commands")
					if commands.commands[match[0]] in commands.flerovium_inc_commands:
						logEntry("Command is incompatible")
						# check if command is incompatible
						return lambda *a: ":no_entry_sign: The command you issued is incompatible with Flerovium."
				if commands.commands[match[0]] in inc_commands:
					logEntry("Command is incompatible")
					return lambda *a: ":no_entry_sign: The command you issued is incompatible with Flerovium."
				else: 
					logEntry("Found in commands")
					return commands.commands[match[0]]
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
				logEntry("Output is empty")
				if len(match) > 1: output=func(assemble_botdata(),{},*match[1:])
				elif func: output=func(assemble_botdata(),{})
				else: output=":no_entry_sign: The command you issued is not on the Flerovium command list."
			
			# send the post
			if type(output)==discord.Embed: await message.channel.send(embed=output)
			elif type(output)==str: 
				if "initial_emoji" in dir(commands): 
					output = commands.initial_emoji + " " + output
					commands.initial_emoji = ""
				output = formatToDiscord(output)
				await message.channel.send(output)
			else: await message.channel.send(output)
			logEntry("Sent "+ repr(output))
			stats["valid_commands"]+=1
			showStats()
		except (TypeError, ValueError, KeyError, IndexError, OverflowError, ZeroDivisionError) as e:
			tb = traceback.format_exc()
			await message.channel.send('While {phase} that command, an error occured:\n```\n{tb}\n```'.format(**{**locals(),**globals()}))
			logEntry("{} while {} command {}: {}".format(type(e).__name__,phase,repr(message),e))
			jump = False
			raise 
		

logEntry("Starting up...")
print("Flerovium - A Discord intergration of Nihonium")
client = Flerovium()
print("Logging in...")
client.run(token)