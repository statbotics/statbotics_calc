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
    return env.create_rating(mu=1450, sigma=sigma_env)


def existing_rating(team):
    mu, sigma, alpha = team.get_rating_max(), team.rating.sigma, 0.25
    mu = (1-alpha) * mu + alpha * (mu_env-100)
    sigma = (1-alpha) * sigma + alpha * sigma_env
    return env.create_rating(mu=mu, sigma=sigma)


def update_rating(year, teams, match):
    r = [teams[match.red[i]].rating for i in range(len(match.red))]
    b = [teams[match.blue[i]].rating for i in range(len(match.blue))]
    match.set_ratings(r, b)

    if match.winner == "red":
        nr, nb = env.rate([r, b], ranks=[1, 0])
    elif match.winner == "blue":
        nb, nr = env.rate([r, b], ranks=[0, 1])
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
