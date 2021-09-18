import json
from datetime import timedelta

with open('dungeons.json', 'r') as file:
    dungeons = json.load(file)
    file.close()

with open('keylvltoscore.json', 'r') as file:
    keylvltoscore = json.load(file)
    file.close()

class MythicRun:
    def __init__(self, rid, pids, pnames, dung, lvl, time, score, timestamp, pclasses):
        self.rid = rid
        self.pids = pids
        self.pnames = pnames
        self.dung = dung
        self.lvl = lvl
        self.time = time
        self.score = score
        self.timestamp = timestamp
        self.pclasses = pclasses

    def updateScore(self):
        for dungeon in dungeons:
            if self.dung == int(dungeon["id"][5:8]):
                dungTimers = dungeon["timer"]

        max_time = dungTimers[0] + 5  # assume max deplete time 5 sec
        deplete_score = keylvltoscore[self.lvl - 2] + 0.01
        timed_score = keylvltoscore[self.lvl]
        up_score = keylvltoscore[self.lvl + 1]

        if self.time >= max_time:  # if went pepegas
            self.score = deplete_score
        elif max_time > self.time > dungTimers[0]:  # if depleted
            self.score = (((self.time - max_time) / (max_time - dungTimers[0])) * (deplete_score - timed_score)) + deplete_score
        else:
            self.score = ((self.time / dungTimers[0]) * (timed_score - up_score)) + up_score

        self.score = round(self.score, 2)


class Player:
    def __init__(self, pid, name, pclass, spec, bruns, fsio):
        self.pid = pid
        self.name = name
        self.pclass = pclass
        self.spec = spec
        self.bruns = bruns
        self.fsio = fsio

    def updatename(self):
        pass

    def updatefsio(self, currentRuns):
        newio = 0
        for rid in self.bruns:
            idx, run = returnRun(currentRuns, rid)

            newio += run.score
        self.fsio = newio
        self.fsio = round(self.fsio, 2)

    # def sanitycheck(self, runList):
    #     newbruns = []
    #     for brun1 in self.bruns:
    #         for brun2 in self.bruns:
    #
    #             if brun1 == brun2:
    #                 continue
    #
    #             if newbruns.count(brun2) > 0:
    #                 continue
    #
    #             _, run1 = returnRun(runList, brun1)
    #             _, run2 = returnRun(runList, brun2)
    #
    #             if (run1.dung == run2.dung) and (run1.lvl < run2.lvl):
    #                 continue
    #
    #             newbruns.append(brun1)
    #
    #     self.bruns = newbruns



def returnPlayer(playerList, id):
    for idx, player in enumerate(playerList):
        if player.pid == id:
            return idx, player
    return None, None


def returnRun(runList, id):
    for idx, run in enumerate(runList):
        if run.rid == id:
            return idx, run
    return None, None

def returnPlayerByName(name, playerlist):
    for idx, player in enumerate(playerlist):
        if player.name == name:
            return player

def returnCompletedDungeons(player, runList):
    completedDungs = []
    for brun in player.bruns:
        idx, run = returnRun(runList, brun)
        for dungeon in dungeons:
            if run.dung == int(dungeon["id"][5:8]):
                completedDungs.append(dungeon["name"])
    return completedDungs

def returnRuns(player, runList):
    completedRuns = []
    for brun in player.bruns:
        idx, run = returnRun(runList, brun)
        completedRuns.append(run)
    return completedRuns

def sanityCheck(runList, playerList):
    for player in playerList:
        player.sanitycheck(runList)
    return playerList

def scaleScore(timer, dungTimers, dungLevel):
    max_time = dungTimers[0] + 600  # assume max deplete time 10 min
    deplete_score = keylvltoscore[dungLevel - 2] + 0.01
    timed_score = keylvltoscore[dungLevel]
    up_score = keylvltoscore[dungLevel + 1]
    if timer >= max_time: # if went pepegas
        return deplete_score
    elif max_time > timer > dungTimers[0]: # if depleted
        return (((timer - max_time) / (max_time - dungTimers[0])) * (deplete_score - timed_score)) + deplete_score
    else:
        return ((timer / dungTimers[0]) * (timed_score - up_score)) + up_score

def printTop(currentPlayers):
    for i in range(10):
        print(str(i+1) +". "+ currentPlayers[i].name + ", " + str(currentPlayers[i].fsio) + ", Completed Dungeons: " + str(len(currentPlayers[i].bruns)))

def getDungName(dungid):
    for dungeon in dungeons:
        if dungid == int(dungeon["id"][5:8]):
            return dungeon["name"]
    return None


def printPlayer(playerName, currentPlayers, currentRuns):
    player = returnPlayerByName(playerName, currentPlayers)
    if player == None:
        print("Player Not Found!")
    print(player.name + ", " + str(player.fsio))
    for rid in player.bruns:
        _ , run = returnRun(currentRuns, rid)
        print(getDungName(run.dung) + ', Level: ' + str(run.lvl) + ', Time: ' + str(timedelta(seconds= run.time)) + ', Score: ' + str(run.score))