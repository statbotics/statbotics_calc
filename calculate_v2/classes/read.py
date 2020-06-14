from classes.classes import (
    Team,
    Year,
    TeamYear,
    Event,
    TeamEvent,
    Match,
    TeamMatch
)


class SQL_Read:
    def __init__(self, SQL):
        self.reads = 0
        self.session = SQL.getSession()

    def getStats(self):
        return self.reads

    '''Team'''

    def getTeam(self, number):
        self.reads += 1
        return self.session.query(Team).filter_by(id=number).first()

    def getTeams(self):
        self.reads += 1
        return self.session.query(Team).order_by('id').all()

    def getTotalTeams(self):
        self.reads += 1
        return self.session.query(Team).count()

    '''Year'''

    def getYear(self, year):
        self.reads += 1
        return self.session.query(Year).filter_by(id=year).first()

    def getYears(self):
        self.reads += 1
        return self.session.query(Year).order_by('id').all()

    def getTotalYears(self):
        self.reads += 1
        return self.session.query(Year).count()

    '''Team Year'''

    def getTeamYear(self, teamYear):
        self.reads += 1
        return self.session.query(TeamYear).filter_by(id=teamYear).first()

    def getTeamYear_byParts(self, team, year):
        self.reads += 1
        return self.session.query(TeamYear) \
            .filter_by(team_id=team, year_id=year).first()

    def getTeamYears(self, team=None, year=None, teamYear=None):
        self.reads += 1
        out = self.session.query(TeamYear)
        if team is not None:
            out = out.filter_by(team_id=team)
        if year is not None:
            out = out.filter_by(year_id=year)
        if teamYear is not None:
            out = out.filter_by(id=teamYear)
        return out.order_by('id').all()

    def getTotalTeamYears(self):
        self.reads += 1
        return self.session.query(TeamYear).count()

    '''Event'''

    def getEvent(self, event):
        self.reads += 1
        return self.session.query(Event).filter_by(id=event).first()

    def getEvent_byKey(self, event_key):
        self.reads += 1
        return self.session.query(Event).filter_by(key=event_key).first()

    def getEvents(self, year=None, event=None):
        self.reads += 1
        out = self.session.query(Event)
        if year is not None:
            out = out.filter_by(year_id=year)
        if event is not None:
            out = out.filter_by(id=event)
        return out.order_by('id').all()

    def getTotalEvents(self):
        self.reads += 1
        return self.session.query(Event).count()

    '''Team Event'''

    def getTeamEvent(self, teamEvent):
        self.reads += 1
        return self.session.query(TeamEvent).filter_by(id=teamEvent).first()

    def getTeamEvent_byParts(self, team, event):
        self.reads += 1
        return self.session.query(TeamEvent) \
            .filter_by(team_id=team, event_id=event).first()

    def getTeamEvents(self, team=None, year=None,
                      teamYear=None, event=None, teamEvent=None):
        self.reads += 1
        out = self.session.query(TeamEvent)
        if team is not None:
            out = out.filter_by(team_id=team)
        if year is not None:
            out = out.filter_by(year_id=year)
        if teamYear is not None:
            out = out.filter_by(team_year_id=teamYear)
        if event is not None:
            out = out.filter_by(event_id=event)
        if teamEvent is not None:
            out = out.filter_by(id=teamEvent)
        return out.order_by('id').all()

    def getTotalTeamEvents(self):
        self.reads += 1
        return self.session.query(TeamEvent).count()

    '''Match'''

    def getMatch(self, match):
        self.reads += 1
        return self.session.query(Match).filter_by(id=match).first()

    def getMatch_byKey(self, match_key):
        self.reads += 1
        return self.session.query(Match).filter_by(key=match_key).first()

    def getMatches(self, year=None, event=None, match=None):
        self.reads += 1
        out = self.session.query(Event)
        if year is not None:
            out = out.filter_by(year_id=year)
        if event is not None:
            out = out.filter_by(event_id=event)
        if match is not None:
            out = out.filter_by(id=match)
        return out.order_by('id').all()

    def getTotalMatches(self):
        self.reads += 1
        return self.session.query(Match).count()

    '''Team Match'''

    def getTeamMatch(self, teamMatch):
        self.reads += 1
        return self.session.query(TeamMatch).filter_by(id=teamMatch).first()

    def getTeamMatches(self, team=None, year=None, teamYear=None, event=None,
                       teamEvent=None, match=None, teamMatch=None):
        self.reads += 1
        out = self.session.query(TeamEvent)
        if team is not None:
            out = out.filter_by(team_id=team)
        if year is not None:
            out = out.filter_by(year_id=year)
        if teamYear is not None:
            out = out.filter_by(team_year_id=teamYear)
        if event is not None:
            out = out.filter_by(event_id=event)
        if teamEvent is not None:
            out = out.filter_by(team_event_id=teamEvent)
        if match is not None:
            out = out.filter_by(match_id=match)
        if teamMatch is not None:
            out = out.filter_by(id=teamMatch)
        return out.order_by('id').all()

    def getTotalTeamMatches(self):
        self.reads += 1
        return self.session.query(TeamMatch).count()