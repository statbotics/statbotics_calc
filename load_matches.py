import math
import datetime
import statistics

import requests

from classes import Match
import utils

'''
Helper class to read the TheBlueAlliance (TBA) API
'''

auth_key = "V3FDGbXKFVDRWOeHmotTdbOFBMZPvwG5VulPsEXFwZ5tI6hxK6FbCgOm200OKLm7"
read_pre = "https://www.thebluealliance.com/api/v3/"

session = requests.Session()
session.headers.update({'X-TBA-Auth-Key': auth_key, 'X-TBA-Auth-Id': ''})

def get(url): return session.get(read_pre+url).json()

def getEvents(year=2020):
    events = []
    for event in get("events/"+str(year)+"/simple"):
        if(event["event_type"]<=10): events.append(event["key"])
    return events

def getEventTime(event):
    date = get("event/"+str(event)+"/simple")["start_date"] #for pre 2016 events
    return int(datetime.datetime.strptime(date, "%Y-%m-%d").timestamp())

def getMatchTime(match, event_time):
    if match["actual_time"]!=None: return match["actual_time"]
    match_time = event_time #start value
    if match["comp_level"]=="qm": match_time += match["match_number"]
    elif match["comp_level"]=="qf": match_time += 200 + 10 * match["set_number"] + match["match_number"]
    elif match["comp_level"]=="sf": match_time += 400 + 10 * match["set_number"] + match["match_number"]
    else: match_time += 600 + match["match_number"]
    return match_time

def getMatchesEvent(year, event):
    matches = []
    event_time = getEventTime(event)
    for match in get("event/"+str(event)+"/matches/simple"):
        match["actual_time"] = getMatchTime(match, event_time) #correctly orders matches pre 2016
        red_teams = len(match["alliances"]["red"]["team_keys"])
        blue_teams = len(match["alliances"]["blue"]["team_keys"])
        if(year>2004 and red_teams==3 and blue_teams==3): matches.append(Match(match))
        elif(year<=2004 and red_teams>=2 and blue_teams>=2): matches.append(Match(match))
    matches.sort()
    return matches

def getMatchesYear(year):
    matches = []
    events = getEvents(year)
    for event in events:
        for match in getMatchesEvent(year, event):
            matches.append(match)
    matches.sort()
    return matches

def saveMatches(start_year, end_year):
    for year in range(start_year, end_year+1):
        matches = getMatchesYear(year)
        utils.saveMatches(year, matches)

def getSD(year):
    scores = []
    for match in getMatchesYear(year):
        scores.append(match.red_score)
        scores.append(match.blue_score)
    return statistics.pstdev(scores)

def getSDs(start_year, end_year):
    for year in range(start_year, end_year+1):
        print(str(year)+":\t"+str(getSD(year)))

def main():
    getSDs(2002, 2020)
    #saveMatches(2002, 2020)

if __name__ == "__main__":
    main()
