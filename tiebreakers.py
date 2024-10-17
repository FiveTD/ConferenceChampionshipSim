# ACC: https://theacc.com/documents/2023/5/17/ACC_FOOTBALL_TIEBREAKER_POLICY.pdf
# Big 12: https://big12sports.com/documents/2024/9/5/Big_12_Football_2024_Tiebreaker_Policy.pdf
# Big Ten: https://bigten.org/fb/article/blt6104802d94ebe1ab/
# SEC: https://www.secsports.com/fbtiebreaker

from model import *
import math

tiebreakers = {
    "ACC" : 
        (None,
         None),
    "B12" :
        (None,
         None),
    "B1G" :
        (None,
         None),
    "SEC" :
        (None,
         None)
}

# === HELPERS ===
def getCommonGames(teams: list[Team]) -> list[Game]:
    games: list[Game] = []
    for i, team in enumerate(teams):
        for opponent in teams[i+1:]:
            game: Game = team.getGameByOpponent(opponent)
            if game is not None: games.append(game)
    return games

def getCommonOpponents(teams: list[Team]) -> list[Game]:
    commonOpponents = teams[0].getOpponents()
    for team in teams[1:]:
        commonOpponents = [o for o in team.getOpponents() if o in commonOpponents]

def sortDictValuesDescending(d: dict) -> dict:
    return dict(sorted(d.items(), key = lambda item: item[1], reverse=True))

# Flatten sorted dict into list with equal values grouped into sublists
def groupDictKeysByValue(d: dict) -> list:
    result = []
    currentGroup = []
    lastValue = d.values()[0]
    for key, value in d:
        if value == lastValue:
            currentGroup.append(key)
        else:
            if currentGroup:
                result.append(currentGroup if len(currentGroup) > 1 else currentGroup[0])
            currentGroup = [key]
            lastValue = value
    result.append(currentGroup if len(currentGroup) > 1 else currentGroup[0])
    return result

class Tiebreaker:
    def __init__(self, conference: Conference) -> None:
        self.conference = conference
        self.tiebreakers = tiebreakers[conference.abbrName]
        
    # Takes in tbIdx: current tiebreaker (recursive)
    # Returns true if top teams are fully separated, false if top teams are unable to be separated
    # Separation fails when tiebreaker is insufficient OR no more tiebreakers
    def orderStandings(self, conference: Conference, tbIdx = 0) -> bool:
        conference.setStandings()
        raise NotImplementedError
        #TODO
    
    # === TIEBREAKER DEFS ===
    
    # If two teams played, advantage winner
    def HeadToHeadTwo(self, teams: list[Team]) -> list:
        game: Game = teams[0].getGameByOpponent(teams[1])
        
        if game is None:
            return [teams]
        elif teams[0] is game.winner:
            return teams
        else:
            return teams.reverse()
    
    # If all teams played each other ('round robin'), advantage in order of wins
    # If not all teams played, advantage team that defeated all other teams
    # No advantage otherwise
    def HeadToHeadMulti(self, teams: list[Team]) -> list:
        nTeams = len(teams)
        games = getCommonGames(teams)
        winTotals = { team: len([g for g in games if g.winner is team]) for team in teams }
        winTotals = sortDictValuesDescending(winTotals)
        
        # All games played ('round robin')
        if len(games) == math.factorial(nTeams) / (2 * math.factorial(nTeams - 2)):
            
            return groupDictKeysByValue(winTotals)
        # Not all games played
        else:
            top = winTotals.items()[0]
            # If one team won against all opponents, advantage them
            if top[1] == nTeams - 1:
                return [top[0], winTotals.keys()[1:]]
            # No team advantaged
            else:
                return [teams]
    
    # If not all teams played each other, disadvantage team that lost to all others
    def HeadToHeadLoserMulti(self, teams: list[Team]) -> list:
        nTeams = len(teams)
        games = getCommonGames(teams)
        winTotals = { team: len([g for g in games if g.winner is team]) for team in teams }
        winTotals = sortDictValuesDescending(winTotals)
        
        bottom = winTotals.items()[-1]
        if bottom[1] == 0 and len([g for g in games if g.played(bottom[0])]) == nTeams - 1:
            return [winTotals.keys()[:-1], bottom[0]]
    
    # Advantage to teams with the best record against common opponents
    def CommonOpponents(self, teams: list[Team]) -> list:
        commonOpponents = getCommonOpponents(teams)
        winTotals = { team: len([w for w in [team.getGameByOpponent(o) for o in commonOpponents] if w is not None and w.winner == team]) for team in teams }
        winTotals = sortDictValuesDescending(winTotals)
        return groupDictKeysByValue(winTotals)
    
    def CommonOpponentsInOrder(self, teams: list[Team]) -> list:
        commonOpponents = getCommonOpponents(teams)
        commonOpponentsOrdered = [o for o in self.conference.standings if o in commonOpponents]
        
        # Some lower level opponents have not been tiebroken - tiebreaker fails
        if len(commonOpponents) > len(commonOpponentsOrdered): return [teams]
        
        #TODO
    
    def CommonOpponentsInOrderCollective(self, teams: list[Team]) -> list:
        pass
    
    def StrengthOfSchedule(self, teams: list[Team]) -> list:
        pass
    
    def TotalWins(self, teams: list[Team]) -> list:
        pass
    
    def StrengthOfScheduleMulti(self, teams: list[Team]) -> list:
        pass
    
    def TotalWinsMulti(self, teams: list[Team]) -> list:
        pass