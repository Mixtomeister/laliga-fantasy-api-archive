from datetime import datetime

import http.client
import json
import os
import subprocess

def run_command(command, cwd=None):
    process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr.decode()}")
    else:
        print(stdout.decode())

if __name__ == "__main__":
    players_data = []

    conn = http.client.HTTPSConnection("api-fantasy.llt-services.com")
    try:
        conn.request("GET", "/api/v3/players")

        response = conn.getresponse()
        data = response.read().decode("utf-8")

        for player in json.loads(data):
            conn.request("GET", f"/api/v3/player/{player['id']}")

            response = conn.getresponse()
            players_data.append(json.loads(response.read().decode("utf-8")))
    finally:
        conn.close()

    now = datetime.now()

    if not os.path.exists(f'/var/lib/laliga-fantasy-api-archive/archive/{now.strftime("%Y%m")}'):
        os.makedirs(f'/var/lib/laliga-fantasy-api-archive/archive/{now.strftime("%Y%m")}')

    if players_data:
        with open(f'/var/lib/laliga-fantasy-api-archive/archive/{now.strftime("%Y%m")}/{now.strftime("%d")}.json', 'w') as f:
            f.write(json.dumps(players_data))

        cwd = os.getcwd()

        run_command("git -C /var/lib/laliga-fantasy-api-archive add .", cwd=cwd)

        commit = f"Snapshot {now.strftime('%Y-%m-%d')}" 
        run_command(f'git -C /var/lib/laliga-fantasy-api-archive commit -m "{commit}"', cwd=cwd)

        run_command("git -C /var/lib/laliga-fantasy-api-archive push", cwd=cwd)
