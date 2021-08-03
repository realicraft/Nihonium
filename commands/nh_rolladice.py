import versions
import random

version = versions.Version(1, 7, 5)
nihonium_minver = versions.Version(0, 9, 0)
alt_minvers = {}

def rollADice(bot_data, thread_data, user_data, action="roll"):
    with open("roll_a_dice.json", "r+", encoding="utf-8") as rollfile:
        roll_data = json.loads(rollfile.read())
    output = ""
    uID = str(user_data["uID"])
    if uID not in roll_data: roll_data[uID] = {"points": 0, "timer": 0}
    if action == "roll":
        roll_data2 = {**roll_data}
        del roll_data2["roll_last"]
        timenow = datetime.datetime.now(tz=datetime.timezone.utc)
        if roll_data[uID]["timer"] > timenow.timestamp(): return "You can't roll right now, you can roll again in about " + str(math.ceil((roll_data[uID]["timer"] - timenow.timestamp())/60)) + " minutes."
        done = False
        while not done:
            done = True
            result = random.randint(1, 10)
            output += "You rolled a " + str(result)
            if result == 1:
                roll_data[uID]["points"] += 1
                output += ", and gained one point."
            elif result == 2:
                roll_data[uID]["points"] += 2
                roll_data[uID]["timer"] = int((timenow + datetime.timedelta(hours=4)).timestamp())
                output += ", and gained two points. You can't roll for the next four hours."
            elif result == 3:
                hold = math.floor((int(timenow.timestamp()) - roll_data["roll_last"])/(60*60))
                roll_data[uID]["points"] += hold
                output += ", and gained " + str(hold) + " point" + ("s" if hold != 1 else "") + "."
            elif result == 4:
                hold = random.randint(1, 10)
                roll_data[random.choice(list(roll_data2.keys()))]["points"] -= hold
                output += ", causing someone random to lose " + str(hold) + " point" + ("s" if hold != 1 else "") + "."
            elif result == 5:
                hold = random.randint(1, 5)
                roll_data[random.choice(list(roll_data2.keys()))]["points"] -= hold
                roll_data[uID]["points"] += hold
                output += ", causing someone random to lose " + str(hold) + " point" + ("s" if hold != 1 else "") + ", and for you to recieve said lost points."
            elif result == 6:
                roll_data[uID]["points"] -= 1
                output += ", and lost one point."
            elif result == 7:
                roll_data[uID]["points"] += 1
                done = False
                output += ", gained one point, and get to roll again!\n"
            elif result == 8:
                roll_data[uID]["points"] += 1
                roll_data[random.choice(list(roll_data2.keys()))]["points"] += 2
                output += ", and gained one point, while someone random gained two."
            elif result == 9:
                hold = (random.randint(1, random.randint(1, 60)))
                roll_data[uID]["points"] += hold
                output += ", and gained points equal to how long you have on the 60 second rule.\n...we'll pretend that's " + str(hold) + "."
            elif result == 10:
                roll_data[uID]["points"] += 10
                roll_data[uID]["timer"] = int((timenow + datetime.timedelta(hours=12)).timestamp())
                output += ", and gained ten points! You can't roll for the next twelve hours, though."
        output += "\nYou now have " + str(roll_data[uID]["points"])+ " point" + ("s" if roll_data[uID]["points"] != 1 else "") + "."
        roll_data["roll_last"] = int(timenow.timestamp())
        with open("roll_a_dice.json", "w", encoding="utf-8") as rollfile:
            rollfile.write(json.dumps(roll_data, indent=4))
    elif action in ["points", "score", "check"]:
        hold = roll_data[uID]["points"]
        output += "You have " + str(hold) + " point" + ("s" if hold != 1 else "") + "."
    elif action in ["scoreboard", "leaderboard", "scores"]:
        output += "Current leaderboard:\n[quote]"
        roll_data2 = {**roll_data}
        del roll_data2["roll_last"]
        #based off of careerkarma.com/blog/python-sort-a-dictionary-by-value/
        for i in sorted(roll_data2, key=lambda x: roll_data[x]["points"]):
            output += str(i) + ": " + str(roll_data2[i]["points"]) + " point" + ("s" if roll_data2[i]["points"] != 1 else "") + "\n"
        output += "[/quote][i](Note: the leaderboard uses user IDs rather than usernames, as that is all that is stored.)[/i]"
    return output

commandlist = {"rolladice": rollADice, "rolldice": rollADice}
ex_commandlist = {}