from __future__ import annotations

import time
import copy
    
class Game:
    def __init__(self, home: Team, away: Team, winner: Team = None):
        self.home = home
        self.away = away
        self.winner = winner
        
    def __str__(self) -> str:
        # sep = "@" # in case of no winner
        # if self.winner is self.home:
        #     sep = "<"
        # elif self.winner is self.away:
        #     sep = ">"
        return f"{self.away.name} @ {self.home.name}"
    
    def __repr__(self) -> str:
        return f"<{str(self)}: Game>"
    
    def __copy__(self) -> Game:
        return Game(self.home, self.away, self.winner)
    
    def played(self, team: Team) -> bool:
        return self.home is team or self.away is team

class Team:
    def __init__(self, name: str, conference: Conference = None) -> None:
        self.name = name
        self.conference = conference
        self.games = []
        self.nonConfWins = 0 # Used in Big 12 tiebreakers
        
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"<{str(self)}: Team>"
    
    def __copy__(self) -> Team:
        copyTeam: Team = Team(self.name)
        copyTeam.nonConfWins = self.nonConfWins
        return copyTeam
        
    def addGame(self, game: Game, propagate: bool = False) -> None:
        if propagate:
            self.conference.addGame(game, True) # will add game to this team via propagation
        else:
            self.games.append(game)
            
    def getOpponents(self) -> list[Team]:
        return [g.home if g.home is not self else g.away
                for g in self.games]
    
    def getGameByOpponent(self, team: str | Team) -> Game | None:
        if isinstance(team, str): team = self.conference.getTeamByName(team)
        return next((g for g in self.games if g.played(team)), None)
            
class Conference:
    def __init__(self, name: str, abbrName: str) -> None:
        self.name = name
        self.abbrName = abbrName
        self.teams = []
        self.games = []
        self.setUpdateTimestamp()
        
    def __str__(self) -> str:
        return self.name    
    
    def __repr__(self) -> str:
        return f"<{str(self)}: Conference>"
    
    def __deepcopy__(self, memo) -> Conference:
        copyConf: Conference = Conference(self.name, self.abbrName)
        for team in self.teams:
            copyTeam = copy.copy(team)
            copyTeam.setConference(copyConf)
            copyConf.addTeam(copy.copy(team))
        for game in self.games:
            copyConf.addGame(copy.copy(game))
        copyConf.setUpdateTimestamp(self.update)
        return copyConf
    
    def addTeam(self, team: Team) -> None:
        self.teams.append(team)
        team.conference = self
        
    def getTeamByName(self, name: str) -> Team | None:
        return next((t for t in self.teams if t.name == name), None)
    
    # Adds a standings field and propogates in arbitrary order.
    # NOTE: Does not sort standings. See Tiebreaker.orderStandings().
    def setStandings(self):
        self.standings = copy.copy(self.teams)
            
    def addGame(self, game: Game, propagate: bool = True) -> None:
        self.games.append(game)
        if propagate:
            game.home.addGame(game, False)
            game.away.addGame(game, False)
            
    def getGameByTeams(self, home: Team, away: Team) -> Game | None:
        return next((g for g in self.games if g.home is home and g.away is away), None)
    
    def getGamesByTeam(self, team: Team | str) -> list[Game]:
        if isinstance(team, str): team = self.getTeamByName(team)
        return [g for g in self.games if g.played(team)]
    
    def getUnplayedGames(self) -> list[Game]:
        return [g for g in self.games if g.winner is None]
            
    def setUpdateTimestamp(self, update: int = None) -> None:
        self.update = int(time.time()) if update is None else update