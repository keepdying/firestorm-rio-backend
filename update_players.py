import dill as pickle
from utils import *
from datetime import datetime, timedelta
import json

with open('dungeons.json', 'r') as file:
    dungeons = json.load(file)
    file.close()

with open('keylvltoscore.json', 'r') as file:
    keylvltoscore = json.load(file)
    file.close()

try:
    with open('runs.pickle', 'rb') as file:
        currentRuns = pickle.load(file)
        file.close()
    print("loaded runs file")
except:
    print("couldn't load runs file")
    exit(1)

try:
    with open('players.pickle', 'rb') as file:
        currentPlayers = pickle.load(file)
        file.close()
    print("loaded players file")
except:
    print("couldn't load players file, creating")
    currentPlayers = []

for run in currentRuns:  # loop through runs
    run.updateScore()  # calculate scores again

    for idx, pid in enumerate(run.pids):  # get pids
        pidx, player = returnPlayer(currentPlayers, pid)  # get player with pid

        if not player:  # if player not exist create a new one
            currentPlayers.append(Player(pid, run.pnames[idx], run.pclasses[idx], None, [run.rid], None))

        else:  # if exists
            currentPlayers[pidx].name = run.pnames[idx]
            if currentPlayers[pidx].pclass is None or currentPlayers[pidx].pclass == "noclass":
                if not run.pclasses is None:
                    currentPlayers[pidx].pclass = run.pclasses[idx]

            playerBruns = currentPlayers[pidx].bruns.copy()

            for idxx, pbrid in enumerate(playerBruns):  # loop through brun ids
                _, cbrun = returnRun(currentRuns, pbrid)  # get run with pbrid

                if pbrid == run.rid:  # skip if run already exists
                    break

                if run.dung == cbrun.dung and run.score < cbrun.score:  # skip if we already have a better run
                    break

                if run.dung == cbrun.dung and run.score >= cbrun.score:  # remove brun if ours better
                    currentPlayers[pidx].bruns.remove(pbrid)

                if idxx == (len(playerBruns) - 1):
                    currentPlayers[pidx].bruns.append(run.rid)
                    break

for player in currentPlayers:
    player.updatefsio(currentRuns)  # calculate scores

newCurrentRuns = []  # Delete unused runs
for idx, run in enumerate(currentRuns):
    loopBreak = False
    for player in currentPlayers:
        for brun in player.bruns:
            if run.rid == brun:
                newCurrentRuns.append(run)
                loopBreak = True
                break
        if loopBreak:
            break

currentRuns.sort(key=lambda x: x.timestamp, reverse=False)
currentPlayers.sort(key=lambda x: x.fsio, reverse=True)

with open('players.pickle', 'wb') as file:
    pickle.dump(currentPlayers, file)
    file.close()
    print("wrote {first} players & closed players file".format(first=len(currentPlayers)))

with open('runs.pickle', 'wb') as file:
    pickle.dump(currentRuns, file)
    file.close()
    print(
        f"there are {(len(currentRuns) - len(newCurrentRuns))} unused entries, wrote {len(currentRuns)} runs & closed runs file")

with open('players.json', 'w') as file:
    json.dump([ob.__dict__ for ob in currentPlayers], file, ensure_ascii=False, indent=4)

with open('runs.json', 'w') as file:
    json.dump([ob.__dict__ for ob in currentRuns], file, ensure_ascii=False, indent=4)

with open('lastUpdated.json', 'w') as file:
    now = datetime.now()
    stime_delta = timedelta(hours=2)
    stime = now + stime_delta
    dt_string = stime.strftime("%d/%m/%Y %H:%M:%S") + " GMT+2"
    json.dump(dt_string, file, ensure_ascii=False, indent=4)

exit()
