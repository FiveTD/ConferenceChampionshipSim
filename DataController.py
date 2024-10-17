# "Static class" that manages data sources and maintains conference data.

import os
import requests
import json, copy
from model import *

KEY = os.environ['CFBD_API']
REQ_HEADERS = {"accept": "application/json", "Authorization": f"Bearer {KEY}"}
API_URL = "https://api.collegefootballdata.com"
YEAR = "2024"

loadedConferences = {}
focusedConference: Conference = None
standingsResults = {}

# Returns a loaded conference by name, if it exists; else returns None
def getConference(abbrName: str) -> Conference | None:
    return loadedConferences[abbrName] if abbrName in loadedConferences \
        else None

# Makes API request and processes JSON
def makeRequest(directory: str, params: dict) -> list:
    r = requests.get(f"{API_URL}/{directory}", params = params, headers = REQ_HEADERS)
    # TODO: error handling
    content = r.content.decode('utf-8')
    return json.loads(content)

# Returns the filename for the associated conference
# Creates any necessary directories
def confFilename(abbrName: str) -> str:
    path = "conferences"
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    return f"{path}/{abbrName}.json"
    
# Constructs a conference and its teams via API call
def conferenceFromAPI(abbrName: str) -> Conference:
    teams = makeRequest("teams", {"conference":abbrName})
    
    conference = Conference(teams[0]['conference'], abbrName)
    for t in teams:
        newTeam = Team(t['school'], conference)
        conference.addTeam(newTeam)
            
    updateStandings(conference)
    
    loadedConferences[abbrName] = conference
    return conference

# Constructs a conference and its teams from an existing file
# Returns None if the file does not exist
def conferenceFromFile(abbrName: str) -> Conference | None:
    try:
        with open(confFilename(abbrName), 'r') as f:
            jsonConf = json.load(f)
    except FileNotFoundError:
        return None
    
    conference = Conference(jsonConf['name'], jsonConf['abbrName'])
    conference.setUpdateTimestamp(jsonConf['update'])
    
    for teamDict in jsonConf['teams']:
        newTeam = Team(teamDict['name'])
        newTeam.nonConfWins = teamDict['nonConfWins']
        conference.addTeam(newTeam)
        
    for gameDict in jsonConf['games']:
        home = conference.getTeamByName(gameDict['home'])
        away = conference.getTeamByName(gameDict['away'])
        winner = conference.getTeamByName(gameDict['winner'])
        conference.addGame(Game(home, away, winner))
        
    loadedConferences[conference.abbrName] = conference
    return conference
    
# Exports a conference and its teams to a file
def conferenceToFile(conference: Conference) -> None:
    jsonConf = copy.copy(conference)
    jsonConf.teams = [{'name': t.name,
                             'nonConfWins': t.nonConfWins}
                            for t in jsonConf.teams]
    jsonConf.games = [{'home': g.home.name,
                             'away': g.away.name,
                             'winner': g.winner.name if g.winner is not None else None}
                            for g in jsonConf.games]
    
    with open(confFilename(conference.abbrName), 'w') as f:
        json.dump(jsonConf.__dict__, f, indent = '\t')

# Updates conference standings via API call
def updateStandings(conference: Conference) -> None:
    params = {"year": YEAR,
              "seasonType": "regular",
              "conference": conference.abbrName}
    games = makeRequest("games", params)
    conference.setUpdateTimestamp()
    
    for game in games:
        home = conference.getTeamByName(game['home_team'])
        away = conference.getTeamByName(game['away_team'])
        
        winner = None
        if game['completed']:
            winner = home if game['home_points'] > game['away_points'] \
                else away
        
        # Manual adjustment to data error: Utah @ Baylor and Arizona @ KSU are non-conference
        if home is not None and away is not None:
            if home.name == 'Utah' and away.name == 'Baylor' \
                or home.name == 'Kansas State' and away.name == 'Arizona':
                    game['conference_game'] = False 
                    
        if game['conference_game']:
            conference.addGame(Game(home, away, winner))
                
        # Tally non-conf (used in Big 12 tiebreakers)    
        else:
            # Both teams in non conference game can be in conference (Baylor @ Utah, Arizona @ KSU)
            if home is not None:
                home.nonConfWins += int(home is winner)
            if away is not None:
                away.nonConfWins += int(away is winner)

# At time of current development (Week 8), there are too many games remaining to simulate before the end of a season
# Current estimates:
# - SEC: 35 years
# - ACC: 279 years
# - Big 12: 8926 years
# - Big Ten: 142808 years
# TODO: develop after setgame functionality is complete
def fullMapStandings() -> None:
    numGamesRemaining = len(focusedConference.getUnplayedGames())
    possibleOutcomes = 2 ** numGamesRemaining
    yearsToComplete = possibleOutcomes / (1000 * 31536000) # Number of seconds in a year at a generous estimate of 1000 sims/second
    
    print(f"A full map would currently take approximately {yearsToComplete:.2f} years to complete")
    print("Check back later :)")