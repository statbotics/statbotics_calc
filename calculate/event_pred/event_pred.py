import random

from event_pred.models import elo as elo_model
from event_pred.models import opr as opr_model
from event_pred.models import rps as rps_model
from event_pred.models import tiebreakers
from helper import utils


def getDicts(SQL_Read, event_key, year):
    sd_score, mean_score = SQL_Read.getYearDict(year=year)
    event, event_id = SQL_Read.getEventDict(str(year) + event_key)
    teams, team_stats = SQL_Read.getTeamsDict(event_id=event_id)
    matches = SQL_Read.getMatchesDict(event_id=event_id)
    team_matches = SQL_Read.getTeamMatchesDict(event_id=event_id)

    # currently empty elims
    oprs, ils = opr_model.get_oprs(
        event, year, matches, [], teams, team_stats, team_matches, mean_score
    )
    elos = elo_model.get_elos(event, matches, teams, team_stats, team_matches)
    teams = oprs.keys()

    rps = rps_model.get_rps(event, matches, teams)
    ties = tiebreakers.get_tiebreakers(event, year, matches, teams)

    return teams, matches, sd_score, oprs, ils, elos, rps, ties


def getCurrStats(index, teams, oprs, ils, elos):
    oprs_curr, ils_curr, elos_curr = {}, {}, {}
    for team in teams:
        oprs_curr[team] = oprs[team][index]
        ils_curr[team] = ils[team][index]
        elos_curr[team] = elos[team][index]
    return oprs_curr, ils_curr, elos_curr


def getPreds(index, quals, oprs_curr, elos_curr, ils_curr, year, sd_score):
    team_matches = {}  # for each match i after index, red and blue teams
    preds = {}  # for each match i after index , win_prob, red rps, blue rps
    for i in range(index, len(quals)):
        m = quals[i]
        red, blue = m["red"], m["blue"]
        red_score = sum([utils.clean(oprs_curr[t][0]) for t in red])
        blue_score = sum([utils.clean(oprs_curr[t][0]) for t in blue])
        red_elo = sum([utils.clean(elos_curr[t]) for t in red])
        blue_elo = sum([utils.clean(elos_curr[t]) for t in blue])

        elo_prob = elo_model.win_prob(red_elo, blue_elo)
        elo_margin = elo_model.win_margin(red_elo, blue_elo, sd_score)
        opr_prob = opr_model.win_prob(red_score, blue_score, year, sd_score)
        win_prob = (elo_prob + opr_prob) / 2
        win_margin = (elo_margin + (red_score - blue_score)) / 2
        red_score = (red_score + blue_score) / 2 + win_margin / 2
        blue_score = (red_score + blue_score) / 2 - win_margin / 2

        red_rp_1 = opr_model.rp_prob([ils_curr[t][0] for t in red])
        red_rp_2 = opr_model.rp_prob([ils_curr[t][1] for t in red])
        blue_rp_1 = opr_model.rp_prob([ils_curr[t][0] for t in blue])
        blue_rp_2 = opr_model.rp_prob([ils_curr[t][1] for t in blue])

        ties_pred = tiebreakers.getOPRTiebreakers(oprs_curr, red, blue, year)
        red_tie, blue_tie = ties_pred

        team_matches[i] = [red, blue]
        preds[i] = [
            round(red_score),
            round(blue_score),
            round(win_prob, 2),
            round(red_rp_1, 2),
            round(red_rp_2, 2),
            round(blue_rp_1, 2),
            round(blue_rp_2, 2),
            round(red_tie, 2),
            round(blue_tie, 2),
        ]

    return team_matches, preds


def meanSim(index, matches, teams, team_matches, preds, rps, ties):
    rps_out, ties_out = {}, {}
    for team in teams:
        rps_out[team] = rps[team][index][0]
        ties_out[team] = ties[team][index][0]
    for i in range(index, len(matches)):
        red, blue = team_matches[i]
        red_rps = preds[i][2] * 2 + preds[i][3] + preds[i][4]
        blue_rps = (1 - preds[i][2]) * 2 + preds[i][5] + preds[i][6]
        for team in teams:
            if team in red:
                rps_out[team] += red_rps
                ties_out[team] += preds[i][7]
            if team in blue:
                rps_out[team] += blue_rps
                ties_out[team] += preds[i][8]
    return rps_out, ties_out


def singleSim(index, matches, teams, team_matches, preds, rps, mean_ties):
    rps_out, ranks_out = {}, {}
    for team in teams:
        rps_out[team] = rps[team][index][0]

    for i in range(index, len(matches)):
        red, blue = team_matches[i]
        red_rps, blue_rps = 0, 0
        if preds[i][2] > random.uniform(0, 1):
            red_rps += 2
        else:
            blue_rps += 2
        if preds[i][3] > random.uniform(0, 1):
            red_rps += 1
        if preds[i][4] > random.uniform(0, 1):
            red_rps += 1
        if preds[i][5] > random.uniform(0, 1):
            blue_rps += 1
        if preds[i][6] > random.uniform(0, 1):
            blue_rps += 1
        for team in red:
            rps_out[team] += red_rps
        for team in blue:
            rps_out[team] += blue_rps

    for team in teams:
        ranks_out[team] = [rps_out[team], mean_ties[team]]
    ranks_out = sorted(ranks_out, key=lambda k: (ranks_out[k][0], ranks_out[k][1]))[
        ::-1
    ]
    ranks_out = {ranks_out[i]: i + 1 for i in range(len(ranks_out))}
    return rps_out, ranks_out


def indexSim(index, iterations, teams, matches, team_matches, preds, rps, ties):
    mean_rps, mean_ties = meanSim(index, matches, teams, team_matches, preds, rps, ties)

    T = len(teams)
    avg_rps, ranks = {}, {}
    for team in teams:
        avg_rps[team] = 0
        ranks[team] = [0 for i in range(T)]

    for i in range(iterations):
        rps_ind, ranks_ind = singleSim(
            index, matches, teams, team_matches, preds, rps, mean_ties
        )
        for team in teams:
            avg_rps[team] += rps_ind[team]
            ranks[team][ranks_ind[team] - 1] += 1

    avg_ranks = {}
    for team in teams:
        avg_rps[team] /= iterations
        ranks[team] = [freq / iterations for freq in ranks[team]]
        avg_ranks[team] = 1 + sum([i * ranks[team][i] for i in range(T)])
    return mean_rps, mean_ties, avg_rps, avg_ranks, ranks


def quickSim(SQL_Read, year, event_key):
    teams, matches, sd_score, oprs, ils, elos, rps, ties = getDicts(
        SQL_Read, event_key, year
    )

    out = {t: [] for t in teams}
    for i in range(len(matches) + 1):
        oprs_c, ils_c, elos_c = getCurrStats(i, teams, oprs, ils, elos)
        team_matches, preds = getPreds(
            i, matches, oprs_c, elos_c, ils_c, year, sd_score
        )
        mean_rps, mean_ties = meanSim(i, matches, teams, team_matches, preds, rps, ties)
        for team in teams:
            out[team].append([mean_rps[team], mean_ties[team]])
    return out


def sim(SQL_Read, year, event_key, iterations=100):
    teams, matches, sd_score, oprs, ils, elos, rps, ties = getDicts(
        SQL_Read, event_key, year
    )

    out = {t: [] for t in teams}
    for i in range(len(matches) + 1):
        oprs_c, ils_c, elos_c = getCurrStats(i, teams, oprs, ils, elos)
        team_matches, preds = getPreds(
            i, matches, oprs_c, elos_c, ils_c, year, sd_score
        )
        mean_rps, mean_ties, avg_rps, avg_ranks, ranks = indexSim(
            i, iterations, teams, matches, team_matches, preds, rps, ties
        )
        for team in teams:
            out[team].append(
                [
                    mean_rps[team],
                    mean_ties[team],
                    avg_rps[team],
                    avg_ranks[team],
                    ranks[team],
                ]
            )
    return out
