from bs4 import BeautifulSoup
from utils import *
from datetime import datetime
import re
import time as sleep
import dill as pickle
import json

from selenium import webdriver

try:
    with open('runs.pickle', 'rb') as file:
        currentRuns = pickle.load(file)
        file.close()
    print("loaded file")
except:
    print("couldn't load file")
    currentRuns = []

with open('dungeons.json', 'r') as file:
    dungeons = json.load(file)
    file.close()

browser = webdriver.Chrome()
browser.get("https://firestorm-servers.com/en/challenge/index")
sleep.sleep(5)
affixes = browser.find_elements_by_css_selector('#challenge-content > div > a')  # get affix ids
for i, affix in enumerate(affixes):
    affixes[i] = int(affix.get_attribute('href')[28:])

# page = requests.get("https://firestorm-servers.com/en/challenge/index")  # get challenges page
total_counter = 0
for dungeon in dungeons:
    counter = 0
    affix_counter = 0
    timestamp_counter = 0
    if dungeon["id"] != "1594_247":
        browser.find_element_by_css_selector("#pve_carousel > a.right.carousel-control").click()
        sleep.sleep(2)
        dungSelector = "#pve_carousel > div > div.item.active > div.img_slider.dungeon_{first} > img".format(
            first=dungeon["id"])
        browser.find_element_by_css_selector(dungSelector).click()
    sleep.sleep(1)
    soup = BeautifulSoup(browser.page_source, "html.parser")  # parse page
    runs_table = soup.find(id="challenge-results")  # find table
    runs_tbody = runs_table.find("tbody").find_all("tr")

    for run in runs_tbody:
        data = run.find_all("td")

        # get timestamp
        timestamp = int(run.attrs['scrap-timestamp'])

        # get player ids
        players_data = data[3].find_all("a", href=True)
        pids = []
        for player in players_data:
            pids.append(re.search(r"[^/]+$", player['href']).group())

        # player names and classes
        pnames = []
        pclasses = []
        for player in players_data:
            pnames.append(player.get_text().strip())
            pclasses.append(player.parent['class'][0][6:])

        # create run time in secs
        time = data[2].get_text().strip()
        time = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time.split(":"))))

        # get key level
        lvl = int(data[1].get_text().strip())

        # calculate score
        score = round(scaleScore(time, dungeon["timer"], lvl), 2)

        # generate rid
        rid = dungeon["id"][5:8] + str(lvl).zfill(2) + str(timestamp) + str(pids[0])
        # ensure to not write a run twice
        if currentRuns:
            for idx, run1 in enumerate(currentRuns):
                if not hasattr(currentRuns[idx], 'timestamp'):
                    currentRuns[idx].timestamp = None

                if not hasattr(currentRuns[idx], 'pclasses'):
                    currentRuns[idx].pclasses = ["noclass", "noclass", "noclass", "noclass", "noclass"]

                if currentRuns[idx].pclasses is None:
                    currentRuns[idx].pclasses = ["noclass", "noclass", "noclass", "noclass", "noclass"]

                if not hasattr(currentRuns[idx], 'affixes'):
                    currentRuns[idx].affixes = None

                # if currentRuns[idx].timestamp is None:
                #     extracted_timestamp = int(run1.rid[5: (len(run1.rid) - len(run1.pids[0]))])
                #     dt_obj = datetime.fromtimestamp(extracted_timestamp)
                #     dt_obj = dt_obj.replace(hour=0, minute=0, second=0)
                #     currentRuns[idx].timestamp = int(dt_obj.timestamp())
                #     timestamp_counter += 1

                if rid == run1.rid:

                    currentRuns[idx]["pids"] = pids
                    currentRuns[idx]["pnames"] = pnames

                    break

                elif idx == (len(currentRuns) - 1):
                    currentRuns.append(
                        MythicRun(rid, pids, pnames, int(dungeon["id"][5:8]), lvl, time, score, timestamp, pclasses,
                                  affixes))
                    counter += 1
                    break

        else:
            counter += 1
            currentRuns.append(
                MythicRun(rid, pids, pnames, int(dungeon["id"][5:8]), lvl, time, score, timestamp, pclasses, affixes))

    print(dungeon["abbr"] + ", " + str(counter) + " new runs added.")
    total_counter += counter
with open('runs.pickle', 'wb') as file:
    pickle.dump(currentRuns, file)
    file.close()
    # browser.close()
    print("wrote {first} new entries with total of {second} & closed runs file".format(first=total_counter,
                                                                                       second=len(currentRuns)))
