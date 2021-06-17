import sys, math, random, os, time, json, requests, pause, datetime, versions
from lxml import html

version = Version(0, 3, 4)

with open("postIDs.json", "r+") as postidfile:
    post_ids = json.loads(postidfile.read())

with open("data.json", "r+") as datafile:
    data = json.loads(datafile.read())

with open("pass.txt", "r") as passfile:
    password = passfile.read()

thread_ids = []
for h in post_ids:
    thread_ids.append(int(h))

cookies = None
uptime = datetime.datetime.now()

mainSession = requests.session()
headers = {'User-Agent': 'Chrome/91.0.4472.77'}

login_req = mainSession.get("https://tbgforums.com/forums/login.php", headers=headers)
cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(mainSession.cookies))

def getReq(*args, **kwargs):
    output = mainSession.get(*args, **kwargs)
    cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(mainSession.cookies))
    return output

def postReq(*args, **kwargs):
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
    with open("data.json", "w") as datafile:
        datafile.write(json.dumps(data))

def parse_command(command):
    global data
    with open("data.json", "r+") as datafile:
        data = json.loads(datafile.read())
    command2 = command["contents"].split("<br>")[0][6:]
    command2 = command2.split("</p>")[0]
    shards = command2.split(" ")
    hold = None
    output = "[quote=" + command["author"] + "]nh!" + command2 + "[/quote]"
    if shards[0] == "coin":
        validCommand()
        output += "\nYou flip a coin, and get " + random.choice(["heads", "tails"]) + "."
    elif (shards[0] == "dice") or (shards[0] == "roll"):
        validCommand()
        hold = []
        for i in range(int(shards[1])):
            hold.append(random.randint(1, int(shards[2])))
        output += "\nYou roll " + shards[1] + "d" + shards[2] + ", and get: [code]" + str(hold)[1:-1] + "[/code]"
    elif shards[0] == "uinfo":
        output = ""
    elif shards[0] == "tinfo":
        output = ""
    elif shards[0] == "bot":
        validCommand()
        output += "\nBot Statistics:\n  Uptime: " + str(datetime.datetime.now() - uptime)
        output += "\n  Parse Cycles: " + str(data["parse_cycles"])
        output += "\n  Commands Found: " + str(data["commands_found"])
        output += "\n  Commands Parsed: " + str(data["commands_parsed"])
        output += "\n  Valid Commands: " + str(data["valid_commands"])
        output += "\n  Threads Parsed: " + str(thread_ids)
    else:
        output = ""
    data["commands_parsed"] += 1
    with open("data.json", "w") as datafile:
        datafile.write(json.dumps(data))
    return output

def main_loop(tID, row):
    global cookies
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
    if post_ids[str(tID)] > (pageCount+1)*25:
        #raise ValueError("Page count for thread with ID " + str(tID) + " too low for known last parsed post")
        writeText(43, 5+(row*2), " ERROR ", 9)
        return None
    else:
        pass
    i = math.ceil((post_ids[str(tID)]-1)/25)-1
    need_to_parse = []
    while (i < pageCount):
        bpage = getReq('https://tbgforums.com/forums/viewtopic.php?id=' + str(tID) + '&p=' + str(i+1), headers=headers, cookies=cookies)
        btree = html.fromstring(bpage.content)
        j = 0
        x = btree.xpath('//div[contains(@class, "blockpost")]')
        while (j < len(x)):
            if (j + (i*25) + 1 <= post_ids[str(tID)]):
                j += 1
                continue
            k = {"author": "", "contents": ""}
            y = x[j].xpath('.//div/div[1]/div/div[2]/div[1]') #get contents of post
            z = x[j].xpath('.//div/div[1]/div/div[1]/dl/dt/strong/a') #get user who posted the post
            k["contents"] = html.tostring(y[0]).decode("utf-8")[28:-18]
            k["author"] = html.tostring(z[0]).decode("utf-8").split(">")[1][0:-3]
            if k["contents"].startswith("<p>nh!"):
                need_to_parse.append(k)
                data["commands_found"] += 1
                with open("data.json", "w") as datafile:
                    datafile.write(json.dumps(data))
                writeText(11, 5+(row*2), str(len(need_to_parse)).rjust(5) + " found.  ")
            j += 1
        i += 1
    post_ids[str(tID)] = j + ((i-1)*25)
    writeText(11, 5+(row*2), str(len(need_to_parse)).rjust(5) + " found.  ")
    writeText(26, 5+(row*2), "  Working...  ")
    parsed = 0
    output = ""
    for l in need_to_parse:
        output2 = parse_command(l)
        if output2 == "":
            pass
        else:
            output += output2
            output += "\n"
        parsed += 1
        writeText(26, 5+(row*2), str(parsed).rjust(4) + " parsed.  ")
    writeText(26, 5+(row*2), str(parsed).rjust(4) + " parsed.  ")
    writeText(43, 5+(row*2), "    OK ", 10)
    writeText(41, 5+(row*2), "≈", 6)
    with open("postIDs.json", "w") as l:
        l.write(json.dumps(post_ids))
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
os.system("title Nihonium (Version " + version + ")")

writeText(0, 1, "Nihonium - A TBGs Bot")
writeText(23, 1, "(Version " + version + ")", 14)
clock()

writeText(0, 2, "Logging in...")
login_req = postReq("https://tbgforums.com/forums/login.php?action=in", data={"req_username": "Nihonium", "req_password": password, "form_sent": 1, "redirect_url": "https://tbgforums.com/forums/viewforum.php?id=2", "login": "Login"}, headers=headers, cookies=cookies)
writeText(0, 2, "Logged in successfully.")
time.sleep(1.5)
clock()
clearLine(2)

for m in range(4, 5+(2*len(thread_ids))):
    writeText(0, m, "█"*50)

while True:
    clock()
    thirtyminutes = datetime.datetime.now() + datetime.timedelta(minutes=30)
    writeText(0, 2, "Running loop...")
    for i in range(len(thread_ids)):
        writeText(2, 5+(i*2), str(thread_ids[i]).center(8))
        writeText(11, 5+(i*2), "  Waiting...  ")
        writeText(26, 5+(i*2), "  Waiting...  ")
        writeText(43, 5+(i*2), "  WAIT ", 3)
        writeText(41, 5+(i*2), "W", 3)
    for j in range(len(thread_ids)):
        writeText(0, 2, "Running loop...")
        do_sixsec = main_loop(thread_ids[j], j)
        sixtyseconds = datetime.datetime.now() + datetime.timedelta(seconds=62)
        if (j+1 == len(thread_ids)) or (do_sixsec == False):
            pass
        else:
            writeText(0, 2, "Waiting for 60-second rule...")
            pause.until(sixtyseconds)
        clock()
    data["parse_cycles"] += 1
    with open("data.json", "w") as datafile:
        datafile.write(json.dumps(data))
    clearLine(2)
    writeText(0, 2, "Sleeping...")
    clock()
    for l in range(5, 0, -1):
        sleeptime = thirtyminutes - datetime.datetime.now()
        sleeptime = sleeptime.total_seconds()
        for k in range(int(sleeptime/l)):
            writeText(13, 2, "(" + str(int(sleeptime-k)) + " seconds left)    ", 13)
            clock()
            time.sleep(1)
    writeText(0, 2, "Logging in...")
    login_req = postReq("https://tbgforums.com/forums/login.php?action=in", data={"req_username": "Nihonium", "req_password": password, "form_sent": 1, "redirect_url": "https://tbgforums.com/forums/viewforum.php?id=2", "login": "Login"}, headers=headers, cookies=cookies)
    writeText(0, 2, "Logged in successfully.")
    time.sleep(1.5)
