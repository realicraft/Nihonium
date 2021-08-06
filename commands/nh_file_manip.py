import versions
import shutil, os, datetime, math, random

version = versions.Version(1, 7, 5)
nihonium_minver = versions.Version(0, 9, 0)
alt_minvers = {}

#from Nihonium
def logEntry(entry: str, timestamp=None): # Used to add entries to the log files.
    if timestamp is None: timestamp = datetime.datetime.now()
    with open("logs/" + timestamp.strftime("%Y%m%d") + ".log", "a", encoding="utf-8") as logfile:
        logfile.write("[" + timestamp.strftime("%I:%M:%S.%f %p") + "] " + entry + "\n")

def text(bot_data, thread_data, user_data, command="read", filename="_", *other):
    # commands:
    # read       | outputs the contents of the file
    # write      | replaces the contents of the file with " ".join(other)
    # append     | add " ".join(other) to the end of the file
    # appendline | add a new line at the end of the file, followed by " ".join(other)
    # insert     | insert " ".join(other[1:]) after character other[0]
    # cut        | cut a section of the file, removing it (clipboard will be emptied on paste)
    # copy       | copy a section of the file, trunciated if it ends outide the file
    # paste      | paste onto the end of the file, fails if the clipboard is empty
    # create     | create a file, fails if it exists
    # duplicate  | duplicate a file, fails if it does not exist
    # delete     | delete a file, fails if it does not exist
    # _.txt is unique in that append and insert behave like write, copy and cut select everything, paste overwrites everything, and create, duplicate, and delete all fail
    if filename == "_":
        if command == "append": command = "write"
        if command == "insert": command = "write"
    if "../" in filename:
        return "No file by the name [i]" + filename + ".txt[/i] exists" + random.choice(("", "", "", "", "", ", cheater", ", Mr. Hackerman"))  + "."
    if filename == "con":
        return "Stop that."
    if command == "read":
        try:
            with open("files/" + filename + ".txt", "r", encoding="utf-8") as file: return "Contents of [i]" + filename + ".txt[/i]: \n" + file.read()
            logEntry("Read file '" + filename + ".txt'")
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "write":
        try:
            with open("files/" + filename + ".txt", "w+", encoding="utf-8") as file:
                file.write(" ".join(other))
                file.seek(0)
                logEntry("Wrote to file '" + filename + ".txt'")
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "append":
        try:
            with open("files/" + filename + ".txt", "a+", encoding="utf-8") as file:
                file.write(" ".join(other))
                file.seek(0)
                logEntry("Wrote to file '" + filename + ".txt'")
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "appendline":
        try:
            with open("files/" + filename + ".txt", "a+", encoding="utf-8") as file:
                file.write("\n")
                file.write(" ".join(other))
                file.seek(0)
                logEntry("Wrote to file '" + filename + ".txt'")
                return "New contents of [i]" + filename + ".txt[/i]: \n" + file.read()
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "insert":
        try:
            with open("files/" + filename + ".txt", "r", encoding="utf-8") as file: temp = file.read()
            with open("files/" + filename + ".txt", "w+", encoding="utf-8") as file: file.write(temp[:other[0]] + " ".join(other[1:]) + temp[other[0]:])
            logEntry("Wrote to file '" + filename + ".txt'")
        except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "create":
        try:
            with open("files/" + filename + ".txt", "x", encoding="utf-8") as file: return "Successfully created [i]" + filename + ".txt[/i]"
            logEntry("Created file '" + filename + ".txt'")
        except IOError: return "A file by the name [i]" + filename + ".txt[/i] already exists."
    elif command == "duplicate":
        if filename == "_": return "Can't duplicate _."
        else:
            try:
                shutil.copy2("files/" + filename + ".txt", "files/copy_" + filename + ".txt")
                logEntry("Copied file '" + filename + ".txt' to 'copy_" + filename + ".txt'")
                return "Successfully duplicated [i]" + filename + ".txt[/i]"
            except FileNotFoundError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    elif command == "delete":
        if filename == "_": return "Can't delete _."
        else:
            try:
                os.remove("files/" + filename + ".txt")
                logEntry("Deleted file '" + filename + ".txt'")
                return "Successfully deleted [i]" + filename + ".txt[/i]"
            except IOError: return "No file by the name [i]" + filename + ".txt[/i] exists."
    else: return "Invalid command: " + command

def files(bot_data, thread_data, user_data, command="read", filename="_.txt", *other):
    # commands:
    # read      | read the hex data of a file
    # rename    | rename a file
    # list      | list all files
    # move      | move a file
    # cut       | cut a section of the file, removing it (clipboard will be emptied on paste)
    # copy      | copy a section of the file, trunciated if it ends outide the file
    # paste     | paste onto the end of the file, fails if the clipboard is empty
    # create    | create a file, fails if it exists
    # duplicate | duplicate a file, fails if it does not exist
    # delete    | delete a file, fails if it does not exist
    if "../" in filename:
        return "No file by the name [i]" + filename + "[/i] exists" + random.choice(("", "", "", "", "", ", cheater", ", Mr. Hackerman"))  + "."
    if filename.startswith("con."):
        return "Stop that."
    if command == "read":
        try:
            with open("files/" + filename, "rb") as file:
                logEntry("Read file '" + filename + "'")
                output = "Contents of [i]" + filename + "[/i]: \n[code]"
                filehex = file.read().hex()
                filehexlist = []
                for i in range(0, len(filehex), 2):
                    filehexlist.append(filehex[i:i+2])
                d = "         x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 xA xB xC xD xE xF\n        ------------------------------------------------\n"
                for j in range(math.ceil(len(filehexlist)/16)):
                    d += "0x" + hex(j)[2:].rjust(3, "0") + "x |"
                    e = ""
                    for k in filehexlist[j*16:(j*16)+16]:
                        e += " " + k
                    d += e.ljust(48)
                    d += " | "
                    for l in filehexlist[j*16:(j*16)+16]:
                        if l == "0a": # newline
                            d += "↕"
                        elif l == "09": # tab
                            d += "↔"
                        elif l == "00": # null
                            d += "Φ"
                        elif int(l, 16) > 126: # outside ascii
                            d += "·"
                        elif int(l, 16) < 32: # before printable
                            d += "•"
                        elif l == "20": # space
                            d += "˽"
                        else: # other
                            m = bytes.fromhex(l)
                            d += m.decode("ASCII")
                    d += "\n"
                d = d[0:-1]
                output += d
                output += "[/code]"
                return output
        except IOError: return "No file by the name [i]" + filename + "[/i] exists."
    elif command == "rename":
        try:
            os.rename("files/" + filename, "files/" + other[0])
            logEntry("Renamed file '" + filename + "' to '" + other[0] + "'")
        except FileNotFoundError: return "No file by the name [i]" + filename + "[/i] exists."
        except FileExistsError: return "A file by the name [i]" + other[0] + "[/i] already exists."
    elif command == "list":
        output = "Files: [quote]"
        for i in os.listdir("files"):
            output += i + "\n"
        output += "[/quote]"
        return output
    elif command == "create":
        try:
            with open("files/" + filename, "x", encoding="utf-8") as file: return "Successfully created [i]" + filename + "[/i]"
            logEntry("Created file '" + filename + "'")
        except IOError: return "A file by the name [i]" + filename + "[/i] already exists."
    elif command == "duplicate":
        if filename == "_": return "Can't duplicate _."
        else:
            try:
                shutil.copy2("files/" + filename, "files/copy_" + filename)
                logEntry("Copied file '" + filename + "' to 'copy_" + filename + "'")
                return "Successfully duplicated [i]" + filename + "[/i]"
            except FileNotFoundError: return "No file by the name [i]" + filename + "[/i] exists."
    elif command == "delete":
        if filename == "_": return "Can't delete _."
        else:
            try:
                os.remove("files/" + filename)
                logEntry("Deleted file '" + filename + "'")
                return "Successfully deleted [i]" + filename + "[/i]"
            except IOError: return "No file by the name [i]" + filename + "[/i] exists."
    else: return "Invalid command: " + command

commandlist = {"text": text, "files": files, "file": files}
ex_commandlist = {}