import shlex
from datetime import datetime
import DataController

# === CONSTANTS ===

SUPPORTED_CONFS = ["ACC", "B12", "B1G", "SEC"]

# === TEXT ===

INPUT_CURSOR = "► "

TITLELINE = "Conference Championship Analyzer - 2024"
SUBTITLE = "Use 'help' for help."
SHORTDESC = {
        '': TITLELINE,
        'help': 'help [command]: Get detailed help on a command.',
        'update': 'update [conference]: Load/update latest conference standings from online.',
        'save': 'save [conference]: Save conference standings to disk.',
        'load': 'load [conference]: Load conference standings from disk.',
        'quit': 'quit: Quit program.'
            }
LONGDESC = {
'':
    f"""
COMMANDS:
{"\n".join([f"  - {SHORTDESC[c]}" for c in SHORTDESC.keys() if c != ''])}""", # Displays a formatted list of all commands in shortdesc with associated descriptions

'help':
    """Arguments:
  - [command]: Command to give detailed help on.
    """,
'update':
    """Arguments:
  - [conference = *]: Name of conference to load/update. If *, update all supported conferences.""",
'save':
    """Arguments:
  - [conference = *]: Name of conference to save. If *, save all conferences in memory.""",
'load':
    """Arguments:
  - [conference = *]: Name of conference to load. If *, load all conferences on disk.""",
'quit': ""
           }

SIMULATION_COMPLETE = "Simulation complete"

def UNRECOGNIZED_COMMAND(command: str) -> str:
    return f"Unrecognized command: {command}"

def BAD_ARGUMENT(arg: str) -> str:
    return f"Error processing argument: {arg}"

def UNSUPPORTED_CONFERENCE(conf: str | list[str]) -> str:
    if len(conf) == 1: conf = conf[0] # Converts list with one item to single str
    
    returnStr = ""
    if type(conf) is str:
        returnStr = f"Unrecognized/unsupported conference: {conf}\n"
    else:
        returnStr = f"Unrecognized/unsupported conferences: {", ".join(conf)}\n"
    returnStr += f"Supported conferences: {", ".join(SUPPORTED_CONFS)}"
    return returnStr

def UNLOADED_CONFERENCE(conf: str) -> str:
    return f"Conference not loaded into memory: {conf}"

def NO_CONFERENCE_FILE(conf: str) -> str:
    return f"Conference not saved on disk: {conf}"
           
def UPDATED_CONFERENCE(conf: str) -> str:
    return f"Updated conference: {conf}"

def SAVED_CONFERENCE(conf: str) -> str:
    return f"Saved conference: {conf}"

def LOADED_CONFERENCE(conf: str, update: int = None) -> str:
    returnStr = f"Successfuly loaded conference: {conf}"
    if update is not None: 
        returnStr += f" (last update: {datetime.fromtimestamp(update).strftime("%a %x, %I:%M%p")})" # ex: Sat 10/12/2024, 8:23PM
    return returnStr

def FOCUSED_CONFERENCE(conf: str) -> str:
    return f"Focused conference: {conf}"

def OUTCOMES_TO_SIMULATE(num: int) -> str:
    return f"Outcomes to simulate: {num}\n" + \
        "Continue? (y/n)"
        
# === HELPERS ===

def checkCommandValid(args: list[str]) -> tuple[bool, str]:
    command = args[0] if args else ''
    if command not in SHORTDESC.keys():
        print(UNRECOGNIZED_COMMAND(command))
        return (False, command)
    return (True, command)

def processConferenceArgs(args: list[str], log: bool = True) -> tuple[bool, list[str]]:
    if not args or args[0] == '*': return (True, SUPPORTED_CONFS.copy())
    
    confs = []
    badConfs = []
    for a in args:
        aUp = a.upper()
        if aUp in SUPPORTED_CONFS:
            confs.append(aUp)
        else:
            badConfs.append(a)
    if badConfs and log: print(UNSUPPORTED_CONFERENCE(badConfs))
    return (False, confs)

# === COMMANDS ===

def help(*args: str):
    valid, command = checkCommandValid(args)
    if not valid: return
        
    print(SHORTDESC[command])
    print(LONGDESC[command])

def update(*args: str, log: bool = True):
    default, confNames = processConferenceArgs(args, log = log)
    
    for cn in confNames:
        DataController.conferenceFromAPI(cn)
        if log: print(UPDATED_CONFERENCE(cn))

    if default: save(log = False)
    else: save(*confNames, log = False)
    
def save(*args: str, log: bool = True):
    default, confNames = processConferenceArgs(args)
    
    for cn in confNames:
        conference = DataController.getConference(cn)
        if cn is None: 
            if not default and log:
                print(UNLOADED_CONFERENCE(cn))
        else:
            DataController.conferenceToFile(conference)
            if log: print(SAVED_CONFERENCE(cn))
    
def load(*args: str, log: bool = True):
    default, confNames = processConferenceArgs(args)
    
    for cn in confNames:
        conference = DataController.conferenceFromFile(cn)
        if conference is None:
            if not default and log:
                print(NO_CONFERENCE_FILE(cn))
        else:
            if log: print(LOADED_CONFERENCE(cn, conference.update))
     
def focus(*args: str, log: bool = True):
    abbrName = args[0].upper()
    
    if abbrName not in SUPPORTED_CONFS:
        if log: print(UNSUPPORTED_CONFERENCE(args[0]))
    else:
        abbrName = abbrName.upper()
        conf = DataController.getConference(abbrName)
        if conf is None:
            if log: print(UNLOADED_CONFERENCE(abbrName))
        else:
            DataController.focusedConference = conf
            if log: print(FOCUSED_CONFERENCE(abbrName))
            
def setgame(*args: str, log: bool = True):
    pass

# Development paused until setgame complete, see: DataController.fullMapStandings()
def fullmap(*args: str, log: bool = True):
    numGamesRemaining = len(DataController.focusedConference.getUnplayedGames())
    possibleOutcomes = 2 ** numGamesRemaining
    
    print(OUTCOMES_TO_SIMULATE(possibleOutcomes))
    cont = input(INPUT_CURSOR)
    if cont[0].lower() == 'n': return
    
    DataController.fullMapStandings()
    if log: print(SIMULATION_COMPLETE)

def simulate(*args: str, log: bool = True):
    if args:
        try:
            numSims = int(args[0])
        except:
            print(BAD_ARGUMENT(args[0]))
            return
    else:
        numSims = 100000
    
def quit(): pass

commands = [help, update, save, load, focus, setgame, fullmap, simulate, quit]

# === CONTROL FLOW ===

def main():
    print(TITLELINE)
    print(SUBTITLE)
    
    load()
    
    quitLoop = False
    while not quitLoop:
        userInput = input(INPUT_CURSOR)
        userCommand = shlex.split(userInput)
        commandFunc = next((c for c in commands if c.__name__ == userCommand[0].lower()), None)
        
        if commandFunc is None: print(UNRECOGNIZED_COMMAND(userCommand[0]))
        elif commandFunc is quit: quitLoop = True
        else: commandFunc(*userCommand[1:])
    
if __name__ == '__main__': main()