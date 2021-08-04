import glob, importlib, versions

_submodules = []
for i in glob.glob("commands/*.py"):
    if (i == "commands/__init__.py") or (i == "commands/framework.py") or (i == "commands\__init__.py") or (i == "commands\framework.py"): continue
    _submodules.append(importlib.import_module("commands." + i[9:-3]))

# This folder is used to define the commands used by Nihonium.
# Editing this file directly is not recommended.

__version__ = versions.Version(2, 0, 0)     # This defines the version of the module's framework.

nihonium_minver = versions.Version(0)
alt_minvers = {}
commands = {}
ex_commands = {}
for j in _submodules:
    commands.update(j.commandlist)
    if j.nihonium_minver > nihonium_minver: nihonium_minver = j.nihonium_minver
    for k in j.ex_commandlist:
        try: ex_commands[k].update(j.ex_commandlist[k])
        except KeyError:
            ex_commands[k] = {}
            ex_commands[k].update(j.ex_commandlist[k])
    for l in j.alt_minvers:
        try: alt_minvers[l] = j.alt_minvers[l]
        except KeyError:
            alt_minvers[l] = {}
            alt_minvers[l] = j.alt_minvers[l]