import sys, math, random, os, time, json, requests, pause, datetime, traceback # built-in modules
import versions, commands # custom modules
import html as html2 # disambiguate from lxml.html
from lxml import html # from import

version = versions.Version(0, 6, 5)

if (commands.nihonium_minver > version):
    raise ValueError("This Nihonium install is of version " + str(version) + ", but the copy of 'commands.py' it's using is of version " + str(commands.nihonium_minver) + ".")

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
        logfile.write("[" + timestamp.strftime("%I:%M:%S.%f %p") + "] " + entry + "\n")
        logfile.seek(0)
        line_count = 0
        for line in logfile: line_count += 1
        writeText(97, 2, str(line_count).rjust(4) + " entries in log file", 0, 7)

def getReq(*args, **kwargs):
    logEntry("Requesting URL: " + args[0])
    output = mainSession.get(*args, **kwargs)
    cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(mainSession.cookies))
    return output

def postReq(*args, **kwargs):
    logEntry("Posting to URL: " + args[0])
    output = mainSession.post(*args, **kwargs)
    cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(mainSession.cookies))
    return output

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

def bell():
    sys.stdout.write("\007")
    sys.stdout.flush()

def clearLine(line):
    moveCursor(0, line)
    sys.stdout.write(" "*120)
    sys.stdout.flush()

def clock():
    writeText(113, 0, datetime.datetime.now().strftime("%I:%M %p"), 12, 7)

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
    "version": version}

def assemble_threaddata(tID):
    return {**post_ids[str(tID)], **{"thread_id": tID}}

def parse_command(command, tID):
    global data
    with open("data.json", "r+", encoding="utf-8") as datafile:
        data = json.loads(datafile.read())
    command2 = command["contents"].split("<br>")[0][6:]
    command2 = command2.split("</p>")[0]
    logEntry("Parsing command: " + str(command2))
    shards = command2.split(" ")
    shards2 = shards[1:]
    for i in range(len(shards2)):
        shards2[i] = html2.unescape(shards2[i])
    hold = None
    if shards[0] in commands.commands:
        validCommand()
        output = "[quote=" + command["author"] + "]nh!" + command2 + "[/quote]\n"
        try:
            output += commands.commands[shards[0]](assemble_botdata(), assemble_threaddata(tID), *shards2)
        except (TypeError, ValueError, KeyError, IndexError, OverflowError, ZeroDivisionError):
            logEntry("Failed to parse command: " + str(command2))
            output += "While parsing that command, an error occured: [code]"
            output += traceback.format_exc().splitlines()[-1]
            output += "[/code]"
    else:
        output = ""
    data["commands_parsed"] += 1
    with open("data.json", "w", encoding="utf-8") as datafile:
        datafile.write(json.dumps(data))
    return output

def main_loop(tID, row):
    global cookies
    writeText(0, 2, "Scraping thread " + str(tID) + "...")
    writeText(11, 5+(row*2), "  Working...  ")
    writeText(26, 5+(row*2), "  Waiting...  ")
    writeText(43, 5+(row*2), "  WORK ", 11)
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
        writeText(43, 5+(row*2), " ERROR ", 9)
        return None
    else:
        pass
    i = math.ceil((post_ids[str(tID)]["recentPost"]-1)/25)-1
    need_to_parse = []
    while (i < pageCount):
        bpage = getReq('https://tbgforums.com/forums/viewtopic.php?id=' + str(tID) + '&p=' + str(i+1), headers=headers, cookies=cookies)
        btree = html.fromstring(bpage.content)
        j = 0
        x = btree.xpath('//div[contains(@class, "blockpost")]')
        while (j < len(x)):
            if (j + (i*25) + 1 <= post_ids[str(tID)]["recentPost"]):
                j += 1
                continue
            k = {"author": "", "contents": "", "postID": 0, "date": "", "internal_postid": 0}
            y = x[j].xpath('.//div/div[1]/div/div[2]/div[1]') #get contents of post
            z = x[j].xpath('.//div/div[1]/div/div[1]/dl/dt/strong/a') #get user who posted the post
            a = x[j].xpath('.//h2/span/span') #get postid
            b = x[j].xpath('.//h2/span/a') #get post date/internal post id
            k["contents"] = html.tostring(y[0]).decode("utf-8")[28:-18]
            k["author"] = html.tostring(z[0]).decode("utf-8").split(">")[1][0:-3]
            k["postID"] = int(html.tostring(a[0]).decode("utf-8")[20:-8])
            k["date"] = html.tostring(b[0]).decode("utf-8").split(">")[1][0:-3].replace("&#8201;", "")
            k["internal_postid"] = int(html.tostring(b[0]).decode("utf-8").split('"')[1].split("p")[-1])
            if k["internal_postid"] > data["recent_post"]: data["recent_post"] = k["internal_postid"]
            if k["contents"].startswith("<p>nh!"):
                need_to_parse.append(k)
                data["commands_found"] += 1
                writeText(11, 5+(row*2), str(len(need_to_parse)).rjust(5) + " found.  ")
            with open("data.json", "w", encoding="utf-8") as datafile:
                datafile.write(json.dumps(data))
            j += 1
        i += 1
    post_ids[str(tID)]["recentPost"] = j + ((i-1)*25)
    writeText(11, 5+(row*2), str(len(need_to_parse)).rjust(5) + " found.  ")
    writeText(26, 5+(row*2), "  Working...  ")
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
        writeText(26, 5+(row*2), str(parsed).rjust(4) + " parsed.  ")
    writeText(26, 5+(row*2), str(parsed).rjust(4) + " parsed.  ")
    writeText(43, 5+(row*2), "    OK ", 10)
    writeText(0, 2, "Posting to thread " + str(tID) + "...")
    writeText(41, 5+(row*2), "≈", 6)
    with open("threadData.json", "w", encoding="utf-8") as l:
        l.write(json.dumps(post_ids, indent=4))
    if output == "":
        writeText(41, 5+(row*2), "-")
        return False
    else:
        post_req = postReq("https://tbgforums.com/forums/post.php?tid=" + str(tID), data={"req_message": output, "form_sent": 1}, headers=headers, cookies=cookies)
        try:
            post_req.raise_for_status()
        except:
            writeText(41, 5+(row*2), "X", 9)
            writeText(43, 5+(row*2), " ERROR ", 9)
            raise
        else:
            writeText(41, 5+(row*2), "√", 10)
        return True
    

os.system("cls")
os.system("title Nihonium (Version " + str(version) + ")")

logEntry("Starting up...")
writeText(0, 1, "Nihonium - A TBGs Bot")
writeText(23, 1, "(Version " + str(version) + ")", 14)
clock()

writeText(0, 2, "Logging in...")
logEntry("Logging in...")
login_req = postReq("https://tbgforums.com/forums/login.php?action=in", data={"req_username": "Nihonium", "req_password": password, "form_sent": 1, "redirect_url": "https://tbgforums.com/forums/viewforum.php?id=2", "login": "Login"}, headers=headers, cookies=cookies)
writeText(0, 2, "Logged in successfully.")
logEntry("Logged in successfully.")
time.sleep(1.5)
clock()
clearLine(2)

for m in range(4, 5+(2*len(thread_ids))):
    writeText(0, m, "█"*50)

while True:
    loopNo += 1
    clock()
    thirtyminutes = datetime.datetime.now() + datetime.timedelta(minutes=30)
    clearLine(2)
    writeText(0, 2, "Running loop...")
    logEntry("Running parse cycle " + str(loopNo) + "...")
    for i in range(len(thread_ids)):
        writeText(2, 5+(i*2), str(thread_ids[i]).center(8))
        writeText(11, 5+(i*2), "  Waiting...  ")
        writeText(26, 5+(i*2), "  Waiting...  ")
        writeText(43, 5+(i*2), "  WAIT ", 3)
        writeText(41, 5+(i*2), "W", 3)
    bell()
    for j in range(len(thread_ids)):
        writeText(0, 2, "Running loop...")
        logEntry("Parsing thread #" + str(thread_ids[j]) + "...")
        do_sixsec = main_loop(thread_ids[j], j)
        sixtyseconds = datetime.datetime.now() + datetime.timedelta(seconds=62)
        if (j+1 == len(thread_ids)) or (do_sixsec == False):
            pass
        else:
            writeText(0, 2, "Waiting for 60-second rule...")
            pause.until(sixtyseconds)
        clock()
    data["parse_cycles"] += 1
    with open("data.json", "w", encoding="utf-8") as datafile:
        datafile.write(json.dumps(data))
    clearLine(2)
    writeText(0, 2, "Sleeping...")
    logEntry("Sleeping...")
    clock()
    try: #allow for graceful exit
        for l in range(5, 0, -1):
            sleeptime = thirtyminutes - datetime.datetime.now()
            sleeptime = sleeptime.total_seconds()
            logEntry("Re-aligned sleep time (" + str(sleeptime) + " seconds)")
            for k in range(int(sleeptime/l)):
                writeText(13, 2, "(" + str(int(sleeptime-k)) + " seconds left)    ", 13)
                clock()
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        raise
    clearLine(2)
    writeText(0, 2, "Logging in...")
    logEntry("Logging in...")
    login_req = postReq("https://tbgforums.com/forums/login.php?action=in", data={"req_username": "Nihonium", "req_password": password, "form_sent": 1, "redirect_url": "https://tbgforums.com/forums/viewforum.php?id=2", "login": "Login"}, headers=headers, cookies=cookies)
    writeText(0, 2, "Logged in successfully.")
    logEntry("Logged in successfully.")
    time.sleep(1.5)
    with open("threadData.json", "r+", encoding="utf-8") as threadfile:
        post_ids = json.loads(threadfile.read())
    thread_ids = []
    for h in post_ids:
        thread_ids.append(int(h))
    for m in range(4, 5+(2*len(thread_ids))):
        writeText(0, m, "█"*50)
