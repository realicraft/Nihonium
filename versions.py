# This file provides an object for version numbers.

class Version:
    def __init__(self, major: int, minor: int=0, patch: int=0, tag: str=""):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.tag = tag
    
    def __repr__(self):
        return "Version(" + str(self.major) + ", " + str(self.minor) + ", " + str(self.patch) + ", " + self.tag + ")"
    
    def __str__(self):
        return str(self.major) + "." + str(self.minor) + "." + str(self.patch) + self.tag
    
    def __len__(self):
        if self.tag == "":
            if self.patch == 0:
                if self.minor == 0: return 1
                else: return 2
            else: return 3
        else: return 4
    
    def __int__(self):
        return self.major
    
    #def __float__(self):
    #    return self.major + (self.minor / (10 ** len(self.minor)))
    
    def __eq__(self, o):
        if type(o) == str:
            if len(o.split(".")) == 3:
                try: return ((int(o.split(".")[0]) == self.major) and (int(o.split(".")[1]) == self.minor) and (int(o.split(".")[2]) == self.patch))
                except ValueError: return NotImplemented
                except: raise
            elif len(o.split(".")) == 2:
                try: return ((int(o.split(".")[0]) == self.major) and (int(o.split(".")[1]) == self.minor))
                except ValueError: return NotImplemented
                except: raise
            elif len(o.split(".")) == 1:
                try: return (int(o.split(".")[0]) == self.major)
                except ValueError: return NotImplemented
                except: raise
            else: return NotImplemented
        elif type(o) == int:
            if (self.minor == 0) and (self.patch == 0): return (self.major == o)
            else: return NotImplemented
        elif type(o) == float:
            if (self.patch == 0): return (float(self) == o)
            else: return NotImplemented
        elif type(o) == Version: return (self.major == o.major) and (self.minor == o.minor) and (self.patch == o.patch)
        else: return NotImplemented
    
    def __lt__(self, o):
        if type(o) == str:
            if len(o.split(".")) == 1:
                try: return (int(o.split(".")[0]) < self.major)
                except ValueError: return NotImplemented
                except: raise
            else: return NotImplemented
        elif type(o) == int:
            if (self.minor == 0) and (self.patch == 0): return (self.major < o)
            else: return NotImplemented
        elif type(o) == Version:
            if (self.major < o.major): return True
            elif (self.major == o.major): 
                if (self.minor < o.minor): return True
                elif (self.minor == o.minor): 
                    if (self.patch < o.patch): return True
                    else: return False
                else: return False
            else: return False
        else: return NotImplemented
    
    def __le__(self, o):
        hold = (self < o)
        hold2 = (self == o)
        if (hold == NotImplemented) or (hold2 == NotImplemented): return NotImplemented
        else: return (hold or hold2)
    
    def __gt__(self, o):
        hold = (self <= o)
        if hold == NotImplemented: return NotImplemented
        else: return not hold
    
    def __ge__(self, o):
        hold = (self < o)
        if hold == NotImplemented: return NotImplemented
        else: return not hold

    def __iter__(self):
        if self.tag == "":
            for i in (self.major, self.minor, self.patch):
                yield i
        else:
            for i in (self.major, self.minor, self.patch, self.tag):
                yield i
    
    def asdict(self):
        return {"major": self.major, "minor": self.minor, "patch": self.patch, "tag": self.tag}

__version__ = Version(1, 1)
