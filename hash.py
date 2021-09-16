from datetime import datetime
import dill as pickle
import json
from utils import *

try:
    with open('runs.pickle', 'rb') as file:
        currentRuns = pickle.load(file)
        file.close()
    print("loaded file")
except:
    print("couldn't load file")
    exit(1)

with open('dungeons.json', 'r') as file:
    dungeons = json.load(file)
    file.close()

try:
    with open('players.pickle', 'rb') as file:
        currentPlayers = pickle.load(file)
        file.close()
    print("loaded players file")
except:
    print("couldn't load players file")
    exit(1)

for rrid, run in enumerate(currentRuns): # loop through runs
    if type(run.rid) == type(1.0):
        new_rid = str(run.dung) + str(run.lvl).zfill(2) + str(int(run.rid)) + str(run.pids[0])
    else:
        new_rid = run.rid

    for idx, pid in enumerate(run.pids): # get pids
        pidx, player = returnPlayer(currentPlayers, pid)  # get player with pid
        if not player:
            exit(1)
        else:
            for idxx, pbrid in enumerate(currentPlayers[pidx].bruns):
                if pbrid == run.rid:  # skip if run already exists
                    currentPlayers[pidx].bruns[idxx] = new_rid
                    break
    currentRuns[rrid].rid = new_rid

with open('players.pickle', 'wb') as file:
    pickle.dump(currentPlayers, file)
    file.close()
    print("wrote {first} players & closed players file".format(first=len(currentPlayers)))

with open('runs.pickle', 'wb') as file:
    pickle.dump(currentRuns, file)
    file.close()
    print(
        f"wrote {len(currentRuns)} runs & closed runs file")

