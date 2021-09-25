import json
from datetime import timedelta

with open('dungeons.json', 'r') as file:
    dungeons = json.load(file)
    file.close()

with open('keylvltoscore.json', 'r') as file:
    keylvltoscore = json.load(file)
    file.close()


class MythicRun:
    def __init__(self, rid, pids, pnames, dung, lvl, time, score, timestamp, pclasses, affixes):
        self.rid = rid
        self.pids = pids
        self.pnames = pnames
        self.dung = dung
        self.lvl = lvl
        self.time = time
        self.score = score
        self.timestamp = timestamp
        self.pclasses = pclasses
        self.affixes = affixes

    def updateScore(self):
        for dungeon in dungeons:
            if self.dung == int(dungeon["id"][5:8]):
                dungTimers = dungeon["timer"]

        max_soft_deplete_time = (dungTimers[0] * 2.5)  # assume max deplete time 5 sec

        soft_deplete_start_score = keylvltoscore[self.lvl - 1] + 0.01
        soft_deplete_125 = (keylvltoscore[self.lvl - 2] + 0.01)
        soft_deplete_150 = 0.01 if (self.lvl - 3) < 0 else (keylvltoscore[self.lvl - 3] + 0.01)
        soft_deplete_200 = 0.01 if (self.lvl - 4) < 0 else (keylvltoscore[self.lvl - 4] + 0.01)
        soft_deplete_250 = 0.01 if (self.lvl - 5) < 0 else (keylvltoscore[self.lvl - 5] + 0.01)

        timed_score = keylvltoscore[self.lvl]
        up_score = keylvltoscore[self.lvl + 1]

        if self.time >= max_soft_deplete_time:  # if went beyond
            self.score = soft_deplete_250

        elif (dungTimers[0] * 2.5) > self.time >= (dungTimers[0] * 2):  # if between (2 - 2.5) * dungtimer
            self.score = (((self.time - (dungTimers[0] * 2.5)) / ((dungTimers[0] * 2.50) - (dungTimers[0] * 2))) * (
                    soft_deplete_250 - soft_deplete_200)) + soft_deplete_250

        elif (dungTimers[0] * 2) > self.time >= (dungTimers[0] * 1.50):  # if between (1.50 - 2) * dungtimer
            self.score = (((self.time - (dungTimers[0] * 2)) / ((dungTimers[0] * 2) - (dungTimers[0] * 1.50))) * (
                    soft_deplete_200 - soft_deplete_150)) + soft_deplete_200

        elif (dungTimers[0] * 1.50) > self.time >= (dungTimers[0] * 1.25):  # if between (1.25 - 1.50) * dungtimer
            self.score = (((self.time - (dungTimers[0] * 1.50)) / ((dungTimers[0] * 1.50) - (dungTimers[0] * 1.25))) * (
                    soft_deplete_150 - soft_deplete_125)) + soft_deplete_150

        elif (dungTimers[0] * 1.25) > self.time > dungTimers[0]:  # if between (1 - 1.25) * dungtimer
            self.score = (((self.time - (dungTimers[0] * 1.25)) / ((dungTimers[0] * 1.25) - dungTimers[0])) * (
                    soft_deplete_125 - soft_deplete_start_score)) + soft_deplete_125
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


def scaleScore(time, dungTimers, lvl):
    max_soft_deplete_time = (dungTimers[0] * 2.5)  # assume max soft deplete time is over 250% of timer.

    soft_deplete_start_score = (keylvltoscore[lvl - 1])
    soft_deplete_125 = (keylvltoscore[lvl - 2])
    soft_deplete_150 = 0.01 if (lvl - 3) < 0 else (keylvltoscore[lvl - 3])
    soft_deplete_200 = 0.01 if (lvl - 4) < 0 else (keylvltoscore[lvl - 4])
    soft_deplete_250 = 0.01 if (lvl - 5) < 0 else (keylvltoscore[lvl - 5])

    timed_score = keylvltoscore[lvl]
    up_score = keylvltoscore[lvl + 1]

    if time >= max_soft_deplete_time:  # if went beyond
        score = soft_deplete_250

    elif (dungTimers[0] * 2.5) > time >= (dungTimers[0] * 2):  # if between (2 - 2.5) * dungtimer
        score = (((time - (dungTimers[0] * 2.5)) / ((dungTimers[0] * 2.50) - (dungTimers[0] * 2))) * (
                soft_deplete_250 - soft_deplete_200)) + soft_deplete_250

    elif (dungTimers[0] * 2) > time >= (dungTimers[0] * 1.50):  # if between (1.50 - 2) * dungtimer
        score = (((time - (dungTimers[0] * 2)) / ((dungTimers[0] * 2) - (dungTimers[0] * 1.50))) * (
                soft_deplete_200 - soft_deplete_150)) + soft_deplete_200

    elif (dungTimers[0] * 1.50) > time >= (dungTimers[0] * 1.25):  # if between (1.25 - 1.50) * dungtimer
        score = (((time - (dungTimers[0] * 1.50)) / ((dungTimers[0] * 1.50) - (dungTimers[0] * 1.25))) * (
                soft_deplete_150 - soft_deplete_125)) + soft_deplete_150

    elif (dungTimers[0] * 1.25) > time > dungTimers[0]:  # if between (1 - 1.25) * dungtimer
        score = (((time - (dungTimers[0] * 1.25)) / ((dungTimers[0] * 1.25) - dungTimers[0])) * (
                soft_deplete_125 - soft_deplete_start_score)) + soft_deplete_125
    else:
        score = ((time / dungTimers[0]) * (timed_score - up_score)) + up_score

    score = round(score, 2)
    return score

def printTop(currentPlayers):
    for i in range(10):
        print(str(i + 1) + ". " + currentPlayers[i].name + ", " + str(
            currentPlayers[i].fsio) + ", Completed Dungeons: " + str(len(currentPlayers[i].bruns)))


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
        _, run = returnRun(currentRuns, rid)
        print(getDungName(run.dung) + ', Level: ' + str(run.lvl) + ', Time: ' + str(
            timedelta(seconds=run.time)) + ', Score: ' + str(run.score))
