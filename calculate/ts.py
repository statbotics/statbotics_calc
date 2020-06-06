import trueskill
import itertools
import math

mu_env = 1500
sigma_env = 250

# ignores draws temporarily
env = trueskill.TrueSkill(mu=mu_env,
                          sigma=sigma_env,
                          beta=sigma_env/2,
                          tau=sigma_env/100,
                          draw_probability=0,
                          backend=None)


def new_rating():
    return env.create_rating(mu=mu_env, sigma=sigma_env)


def mean_reversion():
    return env.create_rating(mu=1400, sigma=sigma_env)


def existing_rating(team_1yr, team_2yr):
    if team_1yr is None:
        mu1, sigma = mean_reversion()
    else:
        mu1, sigma = team_1yr.get_rating_max().mu, team_1yr.rating.sigma

    if team_2yr is None:
        mu2, _ = mean_reversion()
    else:
        mu2, _ = team_2yr.get_rating_max()

    mu = 0.70 * mu1 + 0.30 * mu2

    mu = 0.80 * mu + 0.20 * mean_reversion().mu
    sigma = 0.80 * sigma + 0.20 * mean_reversion().sigma
    return env.create_rating(mu=mu, sigma=sigma)


def update_rating(year, teams, match):
    r = [teams[match.red[i]].rating for i in range(len(match.red))]
    b = [teams[match.blue[i]].rating for i in range(len(match.blue))]
    match.set_ratings(r, b)

    # lower rank is better
    if match.winner == "red":
        nr, nb = env.rate([r, b], ranks=[0, 1])
    elif match.winner == "blue":
        nr, nb = env.rate([r, b], ranks=[1, 0])
    else:
        nr, nb = env.rate([r, b], ranks=[0, 0])

    for i in range(len(match.red)):
        teams[match.red[i]].set_rating(nr[i])
    for i in range(len(match.blue)):
        teams[match.blue[i]].set_rating(nb[i])


def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    denom = math.sqrt(6 * ((sigma_env/2) ** 2) + sum_sigma)  # beta=250
    return trueskill.global_env().cdf(delta_mu/denom)
