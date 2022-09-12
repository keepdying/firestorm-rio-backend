#!/usr/bin/python
import psycopg2
import dill as pickle
from utils import *
from datetime import datetime, timedelta
import json
from tqdm import tqdm
date_end = int(datetime.now().timestamp())



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

with open('lastUpdated.json', 'r') as file:
    date_start = json.load(file)
    file.close()

conn = psycopg2.connect(
    host="localhost",
    database="runs_db",
    user="root",
    password="root"
)

cur = conn.cursor()

def insertToDB(conn, cur, currentRuns):
    for run in tqdm(currentRuns):
        run : MythicRun
        try:
            cur.execute('''
                INSERT INTO public.runs (rid, pids, pnames, dung, lvl, "time", score, pclasses, affixes, timestamp) VALUES (
                '%s', 
                '{"%s", "%s", "%s", "%s", "%s"}'::integer[], 
                '{"%s", "%s", "%s","%s", "%s"}'::character varying[], 
                '%s', 
                '%d'::smallint, 
                '%d'::smallint, 
                '%f'::numeric, 
                '{"%s", "%s", "%s", "%s", "%s"}',
                '{%d, %d, %d, %d}'::smallint[],
                to_timestamp(%d))
                returning rid;
                    ''' % (
                    run.rid, 
                    run.pids[0], run.pids[1], run.pids[2], run.pids[3], run.pids[4], 
                    run.pnames[0], run.pnames[1], run.pnames[2], run.pnames[3], run.pnames[4],
                    run.dung,
                    run.lvl,
                    run.time,
                    run.score,
                    run.pclasses[0], run.pclasses[1], run.pclasses[2], run.pclasses[3], run.pclasses[4],
                    run.affixes[0], run.affixes[1], run.affixes[2], run.affixes[3],
                    run.timestamp
                    )
                    )
        except IndexError:
            cur.execute("ROLLBACK")
        except psycopg2.errors.UniqueViolation:
            cur.execute("ROLLBACK")
    conn.commit()


select_query = "SELECT rid, pids, pnames, dung, affixes FROM public.runs WHERE timestamp BETWEEN to_timestamp({}) AND to_timestamp({});".format(date_start, date_end)
cur.execute(select_query)

fetch = cur.fetchone()
while (fetch is not None):
    print(fetch)
    fetch = cur.fetchone()

cur.close()
conn.close()

# with open('lastUpdated.json', 'w', encoding="utf-8") as file:
    # now = datetime.now()
    # json.dump(int(now.timestamp()), file, ensure_ascii=False, indent=4)