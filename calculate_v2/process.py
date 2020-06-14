import datetime
start = datetime.datetime.now()


def printStats(TBA, SQL_Write, SQL_Read):
    print()

    if TBA is not None:
        print("TBA Calls: " + str(TBA.getStats()[0]))
        print("TBA Cache: " + str(TBA.getStats()[1]))
        print()

    if SQL_Write is not None:
        print("SQL Writes: " + str(SQL_Write.getStats()[0]))
        print("SQL Commits: " + str(SQL_Write.getStats()[1]))

    if SQL_Read is not None:
        print("SQL Reads: " + str(SQL_Read.getStats()))

    if SQL_Write is not None or SQL_Read is not None:
        print()

    print("Total Teams: " + str(SQL_Read.getTotalTeams()))
    print("Total Years: " + str(SQL_Read.getTotalYears()))
    print("Total TeamYears: " + str(SQL_Read.getTotalTeamYears()))
    print("Total Events: " + str(SQL_Read.getTotalEvents()))
    print("Total TeamEvents: " + str(SQL_Read.getTotalTeamEvents()))
    print("Total Matches: " + str(SQL_Read.getTotalMatches()))
    print("Total TeamMatches: " + str(SQL_Read.getTotalTeamMatches()))
    print()

    print("Time Elapsed: " + str(datetime.datetime.now()-start))
    print()


def process(start_year, end_year, TBA, SQL_Write, SQL_Read, clean=True):
    if clean:
        print("Loading Teams")
        for team in TBA.getTeams():
            SQL_Write.addTeam(team, False)
        SQL_Write.commit()

    for year in range(start_year, end_year + 1):
        print("Year " + str(year))
        SQL_Write.addYear({"year": year}, False)

        teamYears = TBA.getTeamYears(year)
        for teamYear in teamYears:
            SQL_Write.addTeamYear(teamYear, False)
        SQL_Write.commit()

        print("    Events")
        events = TBA.getEvents(year)
        for event in events:
            event_key = event["key"]
            print("\tEvent: " + str(event_key))
            event_exists = SQL_Write.addEvent(event, False)
            if not event_exists:
                event_id = SQL_Read.getEvent_byKey(event_key).getId()

                teamEvents = TBA.getTeamEvents(event_key)
                for teamEvent in teamEvents:
                    teamEvent["year"] = year
                    teamEvent["event"] = event_id
                    SQL_Write.addTeamEvent(teamEvent, False)

                matches = TBA.getMatches(event_key)
                for match in matches:
                    match["year"] = year
                    match["event"] = event_id
                    SQL_Write.addMatch(match, False)

        SQL_Write.commit()

        printStats(TBA, SQL_Write, SQL_Read)
    printStats(TBA, SQL_Write, SQL_Read)


# removes REALLY old teams and adds district labels
def post_process(TBA, SQL_Write, SQL_Read):
    teams = SQL_Read.getTeams()

    for team in teams:
        '''Removes Teams Before 2002'''
        years = SQL_Read.getTeamYears(team=team.getNumber())
        if len(years) == 0:
            SQL_Write.remove(team)
        else:
            '''Checks if active in 2020'''
            team.active = 0
            for year in years:
                if year.getId() == 2020:
                    team.active = 1

            '''Retrieves district'''
            district = TBA.getTeamDistrict(team.getNumber())
            team.district = district
    SQL_Write.commit()
    printStats(None, SQL_Write, SQL_Read)