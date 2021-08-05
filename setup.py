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
		
def main():
	def download(url, file):
		with open(file, "wb") as f: f.write(requests.get(url).content)
			
	url = ask("Which source should Flerovium use for its custom modules?",{"Nihonium (more up-to-date, less Discord features)":"https://raw.githubusercontent.com/realicraft/Nihonium/main/","Flerovium (more Discord features, less up-to-date)":"https://raw.githubusercontent.com/Gilbert189/Flerovium/main/","Something else":""})
	if not url: url = input("What source should Flerovium get its modules?\nIt should have the necessary files in root.\n> ")

	for x in ("commands.py","versions.py"):
		print("Downloading %s..."%x)
		download(url + x,x)
		
	print("Done!")
	
main()