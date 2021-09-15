import dill as pickle
from utils import *
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

# currentRuns.sort(key=lambda x: x.rid, reverse=False)
debugrid = 1

for run in currentRuns: # loop through runs
    for idx, pid in enumerate(run.pids): # get pids
        pidx, player = returnPlayer(currentPlayers, pid) #get player with pid
        if run.rid == debugrid:
            print('debug mode')
            print(str(run.dung) + ', '+ str(run.score))
        if not player: # if player not exist create a new one
            currentPlayers.append(Player(pid, run.pnames[idx], None, None, [run.rid], None))
        else: # if exists
            currentPlayers[pidx].name = run.pnames[idx]
            playerBruns = currentPlayers[pidx].bruns.copy()

            if run.rid == debugrid:
                print(currentPlayers[pidx].name)
                print(len(playerBruns))



            for idxx, pbrid in enumerate(playerBruns): # loop through brun ids
                _ , cbrun = returnRun(currentRuns, pbrid) # get run with pbrid
                if run.rid == debugrid:
                    print(str(cbrun.dung) + ', ' + str(cbrun.score))
                if pbrid == run.rid: # skip if run already exists
                    if run.rid == debugrid:
                        print("run already exists")
                    break

                if run.dung == cbrun.dung and run.score < cbrun.score: # skip if we already have a better run
                    if run.rid == debugrid:
                        print("we have better run")
                    break

                if run.dung == cbrun.dung and run.score >= cbrun.score: # remove brun if ours better
                    if run.rid == debugrid:
                        print(idxx)
                        print(len(playerBruns))
                        print("removed brun since ours better")
                    currentPlayers[pidx].bruns.remove(pbrid)
                    if run.rid == debugrid:
                        print(idxx)
                        print(len(playerBruns))

                # if len(currentPlayers[pidx].bruns) == 0:
                #     currentPlayers[pidx].bruns.append(run.rid)
                #     if run.rid == debugrid:
                #         print("appended to empty list")
                #     break

                if idxx == (len(playerBruns) - 1):
                    if run.rid == debugrid:
                        print("appended to list")
                    currentPlayers[pidx].bruns.append(run.rid)
                    break




for player in currentPlayers:
    # player.sanitycheck(currentRuns) # check if we have double runs?
    player.updatefsio(currentRuns) # calculate scores

newCurrentRuns = [] # Delete unused runs
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

currentPlayers.sort(key=lambda x: x.fsio, reverse=True)

with open('players.pickle', 'wb') as file:
    pickle.dump(currentPlayers, file)
    file.close()
    print("wrote {first} players & closed players file".format(first=len(currentPlayers)))

with open('runs.pickle', 'wb') as file:
    pickle.dump(currentRuns, file)
    file.close()
    print(
        f"deleted {(len(currentRuns) - len(currentRuns))} unused entries and wrote {len(currentRuns)} runs & closed runs file")

# currentRuns.sort(key=lambda x: x.rid, reverse=False)
currentPlayers.sort(key=lambda x: x.fsio, reverse=True)

with open('players.json', 'w') as file:
  json.dump([ob.__dict__ for ob in currentPlayers], file, ensure_ascii=False, indent= 4)

with open('runs.json', 'w') as file:
  json.dump([ob.__dict__ for ob in currentRuns], file, ensure_ascii=False, indent= 4)

exit()