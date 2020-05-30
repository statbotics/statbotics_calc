import matplotlib.pyplot as plt
import utils

def getStats(year):
    matches = utils.loadProcessedMatches(year)
    error, true_preds = 0, 0

    for m in matches:
        error += (m.get_win_prob()-m.get_win_actual())**2
        if(m.correct_pred()): true_preds+=1

    mse = error/len(matches)
    acc = true_preds/len(matches)

    return [mse, acc]

def metrics():
    total_mse = 0
    for year in range(2002, 2021):
        print(year)
        mse, acc = getStats(year)
        total_mse = total_mse+mse
        print("Brier: " + str(mse))
        print("Accuracy: " + str(acc))
        print()

    total_mse_sykes = 3.716 #see baseline
    print("Total mse Elo:  " + str(total_mse/19))
    print("Total mse Sykes: " + str(total_mse_sykes/19))

def mean():
    for year in range(2002, 2021):
        print(year)
        teams = utils.loadTeams(year)

        ratings = []
        RDs = []
        for team in teams.values():
            ratings.append(team.get_rating()[0])
            RDs.append(team.get_rating()[1])
        ratings.sort()

        print("Rating Avg: " + str(sum(ratings)/len(ratings)))
        print("RD Avg: " + str(sum(RDs)/len(RDs)))
        print("Elo 1%: " + str(ratings[-int(len(ratings)/100)]))
        #plt.hist(elos)
        #plt.show()

if __name__ == "__main__":
    metrics()
    mean()
