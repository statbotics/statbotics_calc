import numpy as np
import itertools
import math

sd = {2002: 11.3, 2003: 31.4, 2004: 33.7, 2005: 15.5, 2006: 20.5, 2007: 32.9,
    2008: 24.4, 2009: 21.0, 2010: 2.7, 2011: 28.4, 2012: 15.5, 2013: 31.1, 2014: 49.3,
    2015: 33.2, 2016: 27.5, 2017: 70.6, 2018: 106.9, 2019: 17.1, 2020: 58.3}

sd_new = {2002: 11.82, 2003: 32.49, 2004: 39.94, 2005: 20.61, 2006: 23.07, 2007: 39.22,
    2008: 27.47, 2009: 22.18, 2010: 3.69, 2011: 33.73, 2012: 19.23, 2013: 42.04, 2014: 58.73,
    2015: 50.42, 2016: 33.80, 2017: 84.71, 2018: 108.24, 2019: 19.57, 2020: 44.50}

def new_rating():
    return [1450, 350]

def existing_rating(team_1yr, team_2yr):
    c = 200 #to tune
    rating_1yr, RD_1yr = team_1yr
    rating_2yr, RD_2yr = team_2yr
    rating = 0.75 * rating_1yr + 0.25 * rating_2yr #previous seasons elo
    rating = 0.75 * rating + 0.25 * new_rating()[0] #to avoid drift
    RD = min(np.sqrt(RD_1yr**2+c**2), new_rating()[1])
    return [rating, RD]

q = np.log(10)/400

def g(RD): return 1/np.sqrt(1+3*q**2*RD**2/np.pi**2)

def E(rating, opp_rating, opp_RD):
    #return 1/(1+10**(-g(opp_RD)*(rating-opp_rating)/400))
    return 0.004 * (rating-opp_rating)

def d(rating, opp_rating, opp_RD):
    E1 = E(rating, opp_rating, opp_RD)
    d2 = (q**2*g(opp_RD)**2*E1*(1-E1))**-1
    return np.sqrt(d2)

def r1(r, RD, opp_r, opp_RD, s):
    E1 = E(r, opp_r, opp_RD)
    g1 = g(opp_RD)
    d1 = d(r, opp_r, opp_RD)
    return r + q/(1/RD**2+1/d1**2)*g1*(s-E1)

def RD1(r, RD, opp_r, opp_RD):
    d1 = d(r, opp_r, opp_RD)
    return np.sqrt((1/RD**2+1/d1**2)**-1)

def sign(x):
    if(x>0): return 1
    if(x<0): return -1
    return 0

def update_rating(year, teams, match):
    red, blue = [], []
    red_ratings, blue_ratings = [], []
    red_RDs, blue_RDs = [], []

    for i in range(len(match.red)):
        red.append(teams[match.red[i]].rating)
        red_ratings.append(teams[match.red[i]].rating[0])
        red_RDs.append(teams[match.red[i]].rating[1])
    for i in range(len(match.blue)):
        blue.append(teams[match.blue[i]].rating)
        blue_ratings.append(teams[match.blue[i]].rating[0])
        blue_RDs.append(teams[match.blue[i]].rating[1])

    match.set_ratings(red.copy(), blue.copy())

    red_rating = sum(red_ratings)/len(red_ratings)
    blue_rating = sum(blue_ratings)/len(blue_ratings)

    red_RD = sum(red_RDs)/len(red_RDs)
    blue_RD = sum(blue_RDs)/len(blue_RDs)
    win_margin = (match.red_score - match.blue_score)/sd[year]
    win_margin = (1+win_margin)/2

    win_margin = sign(win_margin)*min(abs(win_margin), 1)

    red_rating_new = r1(red_rating, red_RD, blue_rating, blue_RD, win_margin)
    blue_rating_new = r1(blue_rating, blue_RD, red_rating, red_RD, 1-win_margin)

    red_diff = red_rating_new - red_rating
    blue_diff = blue_rating_new - blue_rating

    red_RD_new = RD1(red_rating, red_RD, blue_rating, blue_RD)
    blue_RD_new = RD1(blue_rating, blue_RD, red_rating, red_RD)

    red_RD_diff = red_RD_new - red_RD
    blue_RD_diff = blue_RD_new - blue_RD

    for i in range(len(red)):
        red[i] = [red[i][0]+red_diff, max(red[i][1]+red_RD_diff, 50)]

    for i in range(len(blue)):
        blue[i] = [blue[i][0]+blue_diff, max(blue[i][1]+blue_RD_diff, 50)]


    #pred_win_margin = 4/1000*(sum(r)-sum(b))

    #k = 4 if match.playoff else 12
    #for i in range(len(r)): r[i] = r[i] + k*(win_margin-pred_win_margin)
    #for i in range(len(b)): b[i] = b[i] - k*(win_margin-pred_win_margin)

    match.set_ratings_end(red.copy(), blue.copy())

    for i in range(len(red)): teams[match.red[i]].set_rating(red[i])
    for i in range(len(blue)): teams[match.blue[i]].set_rating(blue[i])

def win_probability(red, blue):
    red_ratings, blue_ratings = [], []
    red_RDs, blue_RDs = [], []

    for i in range(len(red)):
        red_ratings.append(red[i][0])
        red_RDs.append(red[i][1])
    for i in range(len(blue)):
        blue_ratings.append(blue[i][0])
        blue_RDs.append(blue[i][1])
    red_rating = sum(red_ratings)/len(red_ratings)
    blue_rating = sum(blue_ratings)/len(blue_ratings)

    red_RD = sum(red_RDs)/len(red_RDs)
    blue_RD = sum(blue_RDs)/len(blue_RDs)

    g1 = g(np.sqrt(red_RD**2+blue_RD**2))
    return 1/(1+10**(-g1*(red_rating-blue_rating)/400))
