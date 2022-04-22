import sys, math, random, os, time, json, requests, pause, datetime, traceback, asyncio # built-in modules
import versions, commands # custom modules
import html as html2 # disambiguate from lxml.html
from lxml import html # from import
from bs4 import BeautifulSoup # used once

version = versions.Version(0, 12, 1)

with open("botInfo.json", "r", encoding="utf-8") as infofile:
    bot_info = json.loads(infofile.read()) # Info about the bot.

inc_commands = () # Commands this copy is incompatible with.
dis_commands = ("rolladice", "rolldice") # Commands disabled in this copy. Overridden by exc_commands.
exc_commands = {"5893": ("rolladice", "rolldice")} # Commands exclusive to specific threads. In the format {"<threadID>": ("<command_name>")}

if (commands.nihonium_minver > version):
    raise ValueError(f"This Nihonium install is of version {str(version)}, but the copy of 'commands.py' it's using requires at least version {str(commands.nihonium_minver)}.")

if (bot_info["id"] != "nihonium") and (commands.alt_minvers[bot_info["id"]] > version):
    raise ValueError(f"This {bot_info['name']} install is of version {str(version)}, but the copy of 'commands.py' it's using requires at least version {str(commands.alt_minvers[bot_info['id']])}.")

with open("threadData.json", "r+", encoding="utf-8") as threadfile:
    post_ids = json.loads(threadfile.read())

with open("data.json", "r+", encoding="utf-8") as datafile:
    data = json.loads(datafile.read())

with open("pass.txt", "r", encoding="utf-8") as passfile:
    password = passfile.read()

thread_ids = []
for h in post_ids:
    thread_ids.append(int(h))

cookies = None
uptime = datetime.datetime.now()
loopNo = 0

mainSession = requests.session()
headers = {'User-Agent': 'Chrome/91.0.4472.77'}

login_req = mainSession.get("https://tbgforums.com/forums/login.php", headers=headers)
cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(mainSession.cookies))

def logEntry(entry: str, timestamp=None):
    if timestamp is None: timestamp = datetime.datetime.now()
    with open("logs/" + timestamp.strftime("%Y%m%d") + ".log", "a+", encoding="utf-8") as logfile:
        logfile.write("[" + timestamp.strftime("%I:%M:%S.%f %p") + "] " + str(entry) + "\n")
        logfile.seek(0)
        line_count = 0
        for _ in logfile: line_count += 1
        writeText(97, 2, str(line_count).rjust(4) + " entries in log file", 0, 7)

def getReq(*args, **kwargs):
    global cookies
    logEntry("Requesting URL: " + args[0])
    output = mainSession.get(*args, **kwargs)
    cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(mainSession.cookies))
    return output

def postReq(*args, **kwargs):
    global cookies
    logEntry("Posting to URL: " + args[0])
    output = mainSession.post(*args, **kwargs)
    cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(mainSession.cookies))
    return output

siggy = ["lang.en.motd", False, ""]

#motd (function), "---..." (const), name/version (no pass), description (const), on/offline (bool), threads parsed (no pass), misc data (str)
#use None to keep whatever was used previously
def update_sig(_motd, xline, misc):
    global siggy
    full_sig = ""
    if _motd is None: full_sig += siggy[0]
    else:
        _motd2 = _motd()
        full_sig += _motd2
        siggy[0] = _motd2
    full_sig += "\n---------------"
    full_sig += f"\n{bot_info['name']} (version {str(version)})"
    full_sig += f"\n[i]{bot_info['tagline']}[/i]"
    if xline is None: xline = siggy[1]
    if xline is False:
        full_sig += f"\n{bot_info['offline']}"
        siggy[1] = False
    else:
        full_sig += f"\n{bot_info['online']}"
        siggy[1] = True
    full_sig += "\nThreads parsed: " + str(thread_ids)
    if misc is None: misc = siggy[2]
    else: siggy[2] = misc
    full_sig += "\n" + misc
    _ = postReq(f"https://tbgforums.com/forums/profile.php?section=personality&id={bot_info['uid']}", data={"signature": full_sig, "form_sent": 1}, headers=headers, cookies=cookies)

def motd():
    return random.choice(["beep", "a", str(version), ":)", "boop", ":(", ":|", str(loopNo), "Also try "+random.choice(["Minecraft", "Terraria", "Fighting Simulator 3", "Legends of Idleon", "Nickel", "Flerovium", "Grogar", "We Play Cards", "Shef Kerbi News Network"])+"!", "yo", "motd", "today's lucky number: "+str(random.randint(1, random.randint(1, 1000))), "", "lorem ipsum", "so how's your day been", "happy current holiday", repr(version), "You can't roll right now, you can roll again in about 600 minutes.", "You can't roll right now, you can roll again in about 240 minutes."])

def moveCursor(x, y):
    sys.stdout.write("\033[" + str(y) + ";" + str(x) + "H")
    sys.stdout.flush()

#         | dark | bright |
# --------+------+--------+
# black   |   0  |    8   |
# red     |   1  |    9   |
# green   |   2  |   10   |
# yellow  |   3  |   11   |
# blue    |   4  |   12   |
# magenta |   5  |   13   |
# cyan    |   6  |   14   |
# white   |   7  |   15   |

def writeText(x, y, text, fcolor=None, bcolor=None):
    if fcolor == None:
        pass
    elif type(fcolor) != int:
        raise TypeError("writeText()'s 'fcolor' attribute must be an Int or None.")
    elif (fcolor > -1) and (fcolor < 8):
        sys.stdout.write("\033[" + str(fcolor+30) + "m")
    elif (fcolor > 7) and (fcolor < 16):
        sys.stdout.write("\033[" + str(fcolor+22) + ";1m")
    else:
        raise ValueError("writeText()'s 'fcolor' attribute must be between 0 and 15.")
    if bcolor == None:
        pass
    elif type(bcolor) != int:
        raise TypeError("writeText()'s 'bcolor' attribute must be an Int or None.")
    elif (bcolor > -1) and (bcolor < 8):
        sys.stdout.write("\033[" + str(bcolor+40) + "m")
    else:
        raise ValueError("writeText()'s 'bcolor' attribute must be between 0 and 7.")
    moveCursor(x, y)
    sys.stdout.write(text)
    sys.stdout.write("\u001b[0m")
    sys.stdout.flush()

async def writeTextA(x, y, text, fcolor=None, bcolor=None):
    writeText(x, y, text, fcolor, bcolor)

def bell():
    sys.stdout.write("\007")
    sys.stdout.flush()

def clearLine(line):
    moveCursor(0, line)
    sys.stdout.write(" "*120)
    sys.stdout.flush()
    
async def writeLine2(text, fcolor=None, bcolor=None):
    clearLine(2)
    writeText(0, 2, text, fcolor, bcolor)

async def clock():
    while True:
        await writeTextA(113, 1, datetime.datetime.now().strftime("%I:%M %p"), 12, 7)
        await asyncio.sleep(1)

def validCommand():
    data["valid_commands"] += 1
    with open("data.json", "w", encoding="utf-8") as datafile:
        datafile.write(json.dumps(data))

def assemble_botdata():
    return {"uptime": uptime,
    "data": data,
    "thread_ids": thread_ids,
    "post_ids": post_ids,
    "cookies": cookies,
    "session": mainSession,
    "headers": headers,
    "version": version,
    "bot_info": bot_info}

def assemble_threaddata(tID):
    return {**post_ids[str(tID)], **{"thread_id": tID}}

def assemble_userdata(command):
    return {"name": command["author"],
    "uID": command["authorID"]}

def parse_command(command, tID):
    global data
    global post_ids
    with open("data.json", "r+", encoding="utf-8") as datafile:
        data = json.loads(datafile.read())
    command2 = command["contents"][len(bot_info["prefix"]):]
    logEntry("Parsing command: " + str(command2))
    shards = command2.split(" ")
    shards2 = shards[1:]
    for i in range(len(shards2)):
        shards2[i] = html2.unescape(shards2[i])
    if ((shards[0].lower() in commands.commands) or ((bot_info["id"] in commands.ex_commands) and (shards[0].lower() in commands.ex_commands[bot_info["id"]]))) and (shards[0].lower() not in inc_commands) and ((shards[0].lower() not in dis_commands) or ((str(tID) in exc_commands) and (shards[0].lower() in exc_commands[str(tID)]))):
        validCommand()
        output = "[quote=" + command["author"] + "]" + bot_info["prefix"] + command2 + "[/quote]\n"
        try:
            if shards[0].lower() in commands.commands: output2 = commands.commands[shards[0].lower()].run(assemble_botdata(), assemble_threaddata(tID), assemble_userdata(command), *shards2)
            else: output2 = commands.ex_commands[bot_info["id"]][shards[0].lower()].run(assemble_botdata(), assemble_threaddata(tID), assemble_userdata(command), *shards2)
            if output2 == "":
                output = ""
            else:
                output += output2
                data["commands_parsed"] += 1
        except (TypeError, ValueError, KeyError, IndexError, OverflowError, ZeroDivisionError):
            logEntry("Failed to parse command: " + str(command2))
            logEntry("Traceback: "+ traceback.format_exc())
            output += f"{bot_info['onError']}[code]"
            output += traceback.format_exc().splitlines()[-1]
            output += "[/code]"
    else:
        output = ""
    with open("threadData.json", "r+", encoding="utf-8") as threadfile:
        post_ids = json.loads(threadfile.read())
    with open("data.json", "w", encoding="utf-8") as datafile:
        datafile.write(json.dumps(data))
    return output

def find_commands(content):
    global data
    content2 = content["contents"]
    content2 = content2.replace("<p>", "\n").replace("</p>", "\n").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    soup = BeautifulSoup(content2, 'html.parser') # from https://stackoverflow.com/a/15797247
    _ = [div.extract() for div in soup.findAll('div')]
    content2 = str(soup)
    content3 = content2.splitlines()
    collect = []
    for i in range(len(content3)):
        if content3[i].startswith(bot_info["prefix"]):
            collect.append({"author": content["author"], "authorID": content["authorID"], "contents": content3[i], "postID": content["postID"], "date": content["date"], "internal_postid": content["internal_postid"]})
            data["commands_found"] += 1
    return collect

    

def main_loop(tID, row):
    global cookies
    writeText(0, 2, "Scraping thread " + str(tID) + "...")
    writeText(11, 5+(row), "  Working...  ")
    writeText(26, 5+(row), "  Waiting...  ")
    writeText(43, 5+(row), "  WORK ", 11)
    apage = getReq('https://tbgforums.com/forums/viewtopic.php?id=' + str(tID), headers=headers, cookies=cookies)
    atree = html.fromstring(apage.content)
    pageCountEl = atree.xpath('//*[@id="brdmain"]/div[1]/div/div[1]/p[1]/a')
    try:
        pageCountEl = pageCountEl[-2]
        pageCount = pageCountEl.attrib["href"]
    except IndexError:
        pageCount = "?p=1"
    pageCount = int(pageCount.split("=")[-1])
    if post_ids[str(tID)]["recentPost"] > (pageCount+1)*25:
        logEntry("Error: Page count for thread with ID " + str(tID) + " too low for known last parsed post")
        #raise ValueError("Page count for thread with ID " + str(tID) + " too low for known last parsed post")
        writeText(43, 5+(row), " ERROR ", 9)
        return False
    else:
        pass
    i = math.ceil((post_ids[str(tID)]["recentPost"]-1)/25)-1
    need_to_parse = []
    j = 0
    while (i < pageCount):
        bpage = getReq('https://tbgforums.com/forums/viewtopic.php?id=' + str(tID) + '&p=' + str(i+1), headers=headers, cookies=cookies)
        btree = html.fromstring(bpage.content)
        j = 0
        x = btree.xpath('//div[contains(@class, "blockpost")]')
        while (j < len(x)):
            if (j + (i*25) + 1 <= post_ids[str(tID)]["recentPost"]):
                j += 1
                continue
            k = {"author": "", "authorID": 0, "contents": "", "postID": 0, "date": "", "internal_postid": 0}
            y = x[j].xpath('.//div/div[1]/div/div[2]/div[1]') #get contents of post
            z = x[j].xpath('.//div/div[1]/div/div[1]/dl/dt/strong/a') #get user who posted the post
            a = x[j].xpath('.//h2/span/span') #get postid
            b = x[j].xpath('.//h2/span/a') #get post date/internal post id
            k["contents"] = html.tostring(y[0]).decode("utf-8")[28:-18]
            k["author"] = html.tostring(z[0]).decode("utf-8").split(">")[1][0:-3]
            k["authorID"] = int(html.tostring(z[0]).decode("utf-8").split('"')[1].split("=")[1])
            k["postID"] = int(html.tostring(a[0]).decode("utf-8")[20:-8])
            k["date"] = html.tostring(b[0]).decode("utf-8").split(">")[1][0:-3].replace("&#8201;", "")
            k["internal_postid"] = int(html.tostring(b[0]).decode("utf-8").split('"')[1].split("p")[-1])
            if k["internal_postid"] > data["recent_post"]: data["recent_post"] = k["internal_postid"]
            #if k["contents"].startswith("<p>" + bot_info["prefix"]):
            #    need_to_parse.append(k)
            #    data["commands_found"] += 1
            #    writeText(11, 5+(row), str(len(need_to_parse)).rjust(5) + " found.  ")
            commands_found = find_commands(k)
            if len(commands_found) != 0:
                for n in commands_found:
                    need_to_parse.append(n)
            writeText(11, 5+(row), str(len(need_to_parse)).rjust(5) + " found.  ")
            with open("data.json", "w", encoding="utf-8") as datafile:
                datafile.write(json.dumps(data))
            j += 1
        i += 1
    new_recent_postid = j + ((i-1)*25)
    post_ids[str(tID)]["recentPost"] = new_recent_postid
    writeText(11, 5+(row), str(len(need_to_parse)).rjust(5) + " found.  ")
    writeText(26, 5+(row), "  Working...  ")
    clearLine(2)
    writeText(0, 2, "Parsing thread " + str(tID) + "...")
    parsed = 0
    output = ""
    for l in need_to_parse:
        output2 = parse_command(l, tID)
        if output2 == "":
            pass
        else:
            output += output2
            output += "\n"
        parsed += 1
        writeText(26, 5+(row), str(parsed).rjust(4) + " parsed.  ")
    writeText(26, 5+(row), str(parsed).rjust(4) + " parsed.  ")
    writeText(43, 5+(row), "    OK ", 10)
    writeText(0, 2, "Posting to thread " + str(tID) + "...")
    writeText(41, 5+(row), "≈", 6)
    post_ids[str(tID)]["recentPost"] = new_recent_postid
    with open("threadData.json", "w", encoding="utf-8") as l:
        l.write(json.dumps(post_ids, indent=4))
    if output == "":
        writeText(41, 5+(row), "-")
        return False
    else:
        post_req = postReq("https://tbgforums.com/forums/post.php?tid=" + str(tID), data={"req_message": output, "form_sent": 1}, headers=headers, cookies=cookies)
        try:
            post_req.raise_for_status()
        except:
            writeText(41, 5+(row), "X", 9)
            writeText(43, 5+(row), " ERROR ", 9)
            raise
        else:
            writeText(41, 5+(row), "√", 10)
        return True
    
#from https://stackoverflow.com/a/2084628
os.system('cls' if os.name == 'nt' else 'clear')
#from https://stackoverflow.com/a/2330596
if os.name == "nt":
    os.system("title " + bot_info["name"] + " (Version " + str(version) + ")")
else:
    sys.stdout.write("\x1b]2;" + bot_info["name"] + " (Version " + str(version) + ")\x07")

logEntry("Starting up...")
writeText(0, 1, "" + bot_info["name"] + " - A TBGs Bot")
writeText(23, 1, "(Version " + str(version) + ")", 14)

writeText(0, 2, "Logging in...")
logEntry("Logging in...")
login_req = postReq("https://tbgforums.com/forums/login.php?action=in", data={"req_username": bot_info["username"], "req_password": password, "form_sent": 1, "redirect_url": "https://tbgforums.com/forums/viewforum.php?id=2", "login": "Login"}, headers=headers, cookies=cookies)
writeText(0, 2, "Logged in successfully.")
logEntry("Logged in successfully.")
time.sleep(1.5)
clearLine(2)

update_sig(motd, True, None)

for m in range(4, 6+len(thread_ids)):
    writeText(0, m, "█"*50)

async def true_main_loop():
    global loopNo
    global thread_ids
    global post_ids
    try: #ugh
        while True:
            loopNo += 1
            thirtyminutes = datetime.datetime.now() + datetime.timedelta(minutes=30)
            clearLine(2)
            writeText(0, 2, "Running loop...")
            logEntry("Running parse cycle " + str(loopNo) + "...")
            for i in range(len(thread_ids)):
                await writeTextA(2, 5+i, str(thread_ids[i]).center(8))
                await writeTextA(11, 5+i, "  Waiting...  ")
                await writeTextA(26, 5+i, "  Waiting...  ")
                await writeTextA(43, 5+i, "  WAIT ", 3)
                await writeTextA(41, 5+i, "W", 3)
            bell()
            update_sig(motd, None, None)
            await writeLine2("Performing do_first functions...")
            for k in commands.do_first:
                k()
            for j in range(len(thread_ids)):
                await writeTextA(0, 2, "Running loop...")
                logEntry("Parsing thread #" + str(thread_ids[j]) + "...")
                do_sixsec = main_loop(thread_ids[j], j)
                sixtyseconds = datetime.datetime.now() + datetime.timedelta(seconds=62)
                if (j+1 == len(thread_ids)) or (do_sixsec == False):
                    pass
                else:
                    await writeTextA(0, 2, "Waiting for 60-second rule...")
                    pause.until(sixtyseconds)
            data["parse_cycles"] += 1
            with open("data.json", "w", encoding="utf-8") as datafile:
                datafile.write(json.dumps(data))
            await writeLine2("Performing do_last functions...")
            for l in commands.do_last:
                l()
            await writeLine2("Sleeping...")
            logEntry("Sleeping...")
            for l in range(5, 0, -1):
                sleeptime = thirtyminutes - datetime.datetime.now()
                sleeptime = sleeptime.total_seconds()
                logEntry("Re-aligned sleep time (" + str(sleeptime) + " seconds)")
                for k in range(int(sleeptime/l)):
                    await writeTextA(13, 2, "(" + str(int(sleeptime-k)) + " seconds left)    ", 13)
                    await asyncio.sleep(1)
            await writeLine2("Logging in...")
            logEntry("Logging in...")
            login_req = postReq("https://tbgforums.com/forums/login.php?action=in", data={"req_username": bot_info["username"], "req_password": password, "form_sent": 1, "redirect_url": "https://tbgforums.com/forums/viewforum.php?id=2", "login": "Login"}, headers=headers, cookies=cookies)
            _ = login_req #suppress unused variable warning
            await writeTextA(0, 2, "Logged in successfully.")
            logEntry("Logged in successfully.")
            await asyncio.sleep(1.5)
            with open("threadData.json", "r+", encoding="utf-8") as threadfile:
                post_ids = json.loads(threadfile.read())
            thread_ids = []
            for h in post_ids:
                thread_ids.append(int(h))
            update_sig(None, None, None)
            for m in range(4, 6+len(thread_ids)):
                await writeTextA(0, m, "█"*50)
    except (KeyboardInterrupt, EOFError): #from https://stackoverflow.com/a/31131378
        time.sleep(1)

async def outerloop():
    await asyncio.gather(*(true_main_loop(), clock()))

def final():
    clearLine(2)
    writeText(1, 2, "Closing...")
    update_sig(None, False, None)
    logEntry("Script closed")
    writeText(1, 2, "Closed.")

async def exit_script():
    loop = asyncio.get_event_loop()
    loop.stop()

#from https://stackoverflow.com/a/54528397
loop = asyncio.get_event_loop()
try:
    clock_future = asyncio.ensure_future(clock())
    loop.run_until_complete(true_main_loop())
except KeyboardInterrupt:
    clock_future.cancel()
    asyncio.ensure_future(exit_script())
finally:
    final()
    moveCursor(0, 6+len(thread_ids))