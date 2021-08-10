"""
This script is for setting up custom modules (like commands.py).
If you're running this on any Python package manager, stop it now. (because you're weird)
"""

import sys, requests

def ask(question, answers: dict, hideUI=False, printer=print, fancy=True):
	if not hideUI:
		printer(question)
		numLen = len(str(len(answers.keys())-1)) + 1
		if fancy:
			strLen = len(sorted(answers.keys(), key=lambda a: len(a), reverse=True)[0]) + 1
			print(f"┌{'─' * numLen}─┬─{'─' * strLen}┐")
			for a, x in enumerate(answers):
				print(f"│{str(a).rjust(numLen)} │ {x.ljust(strLen)}│")
			print(f"└{'─' * numLen}─┴─{'─' * strLen}┘")
		else:
			for a, x in enumerate(answers):
				print(f"{str(a).rjust(numLen)} : {x}")
	try: ans = int(input("> "))
	except: 
		print("Invalid input!")
		return ask(question, answers, hideUI=True)
	return answers[list(answers.keys())[ans]]


for x in ("build", "install", "sdist", "upload"):
	if x in sys.argv: 
		print("This script is for setting up custom modules (like commands.py), not for installing Flerovium like a package.")
		if input("Anyway, shall we continue the procedure? ").lower() not in ("yes", "true", 'y'): exit()
		break
		
def download(url, file):
    with open(file, "wb") as f: f.write(requests.get(url).content)
        
# Order: (user, repo, branch)
url = ask("Which source should Flerovium use for its custom modules?",{"Nihonium (more up-to-date, less Discord features)":("realicraft","Nihonium","main"),"Flerovium (more Discord features, less up-to-date)":("Gilbert189","Flerovium","main")})

for x in ("versions.py",):
    print("Downloading %s..."%(x))
    download("https://raw.githubusercontent.com/" + "/".join(url) + "/" + x,x)
    
try:
    from gitdir import gitdir
    for x in ("commands",):
        print("Downloading directory %s..."%x)
        gitdir.download("https://github.com/" + url[0] + "/" + url[1] + "/tree/" + url[2] + "/" + x)
except ImportError: print("gitdir not found, skipping directory download.\n(You should be able to install it by pip.)")
    
print("Done!")
	