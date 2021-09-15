import dill as pickle
import json

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
    exit(1)

currentRuns.sort(key=lambda x: x.rid, reverse=False)
currentPlayers.sort(key=lambda x: x.fsio, reverse=True)

with open('players.json', 'w') as file:
  json.dump([ob.__dict__ for ob in currentPlayers], file, ensure_ascii=False, indent= 4)

with open('runs.json', 'w') as file:
  json.dump([ob.__dict__ for ob in currentRuns], file, ensure_ascii=False, indent= 4)