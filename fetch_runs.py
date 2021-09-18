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

# page = requests.get("https://firestorm-servers.com/en/challenge/index")  # get challenges page
counter = 0
for dungeon in dungeons:

    if dungeon["id"] != "1594_247":
        browser.find_element_by_css_selector("#pve_carousel > a.right.carousel-control").click()
        sleep.sleep(3)
        dungSelector = "#pve_carousel > div > div.item.active > div.img_slider.dungeon_{first} > img".format(
            first=dungeon["id"])
        browser.find_element_by_css_selector(dungSelector).click()
    sleep.sleep(5)
    soup = BeautifulSoup(browser.page_source, "html.parser")  # parse page
    runs_table = soup.find(id="challenge-results")  # find table
    runs_tbody = runs_table.find("tbody").find_all("tr")

    for run in runs_tbody:
        data = run.find_all("td")

        # create rid
        date_str = data[2].get_text().strip() + ", " + data[4].get_text().strip()
        date_object = datetime.strptime(date_str, "%H:%M:%S, %B %d, %Y")
        rid = date_object.timestamp()

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

        # generate rid p2
        rid = dungeon["id"][5:8] + str(lvl).zfill(2) + str(int(rid)) + str(pids[0])
        # ensure to not write a run twice
        if currentRuns:
            for idx, run1 in enumerate(currentRuns):
                if not hasattr(currentRuns[idx], 'timestamp'):
                    currentRuns[idx].timestamp = None

                if not hasattr(currentRuns[idx], 'pclasses'):
                    currentRuns[idx].pclasses = None

                if rid == run1.rid:

                    if currentRuns[idx].timestamp is None:
                        currentRuns[idx].timestamp = timestamp

                    if currentRuns[idx].pclasses is None:
                        currentRuns[idx].pclasses = pclasses

                    break

                elif idx == (len(currentRuns) - 1):
                    currentRuns.append(
                        MythicRun(rid, pids, pnames, int(dungeon["id"][5:8]), lvl, time, score, timestamp, pclasses))
                    counter += 1
                    break

        else:
            counter += 1
            currentRuns.append(
                MythicRun(rid, pids, pnames, int(dungeon["id"][5:8]), lvl, time, score, timestamp, pclasses))

with open('runs.pickle', 'wb') as file:
    pickle.dump(currentRuns, file)
    file.close()
    browser.close()
    print("wrote {first} new entries with total of {second} & closed runs file".format(first=counter,
                                                                                       second=len(currentRuns)))
