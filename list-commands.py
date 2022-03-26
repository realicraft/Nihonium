"""Lists all available Flerovium commands."""
import json, commands, cli

with open("config.json", "r") as f:
    config = json.loads(f.read())
    for k, v in config.items(): globals()[k] = v

result = {}
for k, v in {**commands.commands,**commands.ex_commands[bot_info["id"]]}.items():
    result[k] = {
        "shortDescription": cli.formatToDiscord(v.help['s']),
        "longDescription": cli.formatToDiscord(v.help['l']),
        "inputs": [{
            "name": x.name,
            "description": cli.formatToDiscord(x.desc),
            "type": x.type
        } for x in v.inputs]
    }

print(json.dumps(result))
