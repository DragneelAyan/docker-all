Scenario-3:
Scenario 3 is where your brain finally “gets” why containers should never store important data inside themselves — because containers die, restart, get replaced, and their internal filesystem gets wiped out.
After Scenario 3, you’ll understand:
✔ Container file system = ephemeral
 ✔ Why logs disappear after redeploy
 ✔ Why DBs and apps must use volumes
 ✔ How Docker mounts work
 ✔ How this maps to Kubernetes PV/PVC
Let’s go step-by-step hands-on again.
SCENARIO 3 — “Logs disappear after redeploy. Fix it using volumes.”
GOAL OF THE EXERCISE
Create a simple container that writes logs to a file inside itself


Delete and restart the container → logs disappear


Attach a persistent volume


Logs survive container deletion


This is a real DevOps issue — happens in AKS, Docker, ECS, everywhere.
STEP 1 — Create scenario3 folder
cd "D:\AZURE IS\DEVOPS\docker-all"
mkdir scenario3
cd scenario3
STEP 2 — Create a simple logging app
Create app.py:
from time import sleep, time

while True:
    with open("app.log", "a") as f:
        f.write(f"Log entry at {time()}\n")
    sleep(2)

This script writes one log entry every 2 seconds.
STEP 3 — Create Dockerfile
FROM python:3.10
WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]
STEP 4 — Build the image
docker build -t logapp .

STEP 5 — Run container normally (NO volume)
docker run -d --name logtest logapp

This runs the container in the background.
STEP 6 — Check logs inside container
Open a shell:
docker exec -it logtest sh

Inside the container:
cat app.log

You will see multiple log entries.
Exit:
exit
STEP 7 — Remove the container (simulate redeploy)
docker rm -f logtest
Container is gone.
STEP 8 — Run a new container without volume
docker run -d --name logtest logapp
Enter:
docker exec -it logtest sh

Check logs:
cat app.log
❌ All logs are gone.
Why?
Because the container internal filesystem is ephemeral → deleted when the container dies.
This is why storing logs, DB data, or uploaded files inside containers is WRONG.
This is also why Kubernetes provides PV/PVC for persistence.
NOW THE FIX — Use Docker Volume
This is the main learning of Scenario 3.
STEP 9 — Create a persistent Docker volume
docker volume create appdata

Docker creates a persistent folder on your host (Windows).
 This folder outlives containers.
STEP 10 — Run container with volume mounted
docker run -d --name logtest -v appdata:/app logapp
Meaning:
You map host volume → container path /app


Now logs are stored in host, NOT inside container


So even if a container dies, logs stay.
STEP 11 — Check logs
Enter container:
docker exec -it logtest sh
cat app.log
You’ll see logs writing every 2 seconds.
STEP 12 — Now delete the container
docker rm -f logtest
Logs on host remain.
STEP 13 — Start a new container with same volume
docker run -d --name logtest -v appdata:/app logapp
Check logs:
docker exec -it logtest sh
cat app.log
You will see the old logs PLUS new ones.
🎉 Persistence achieved.
SCENARIO 3 SUMMARY (Important for interviews)
Action
Result
Container writes logs inside itself
Logs disappear after container removal
Create Docker volume
Host creates persistent storage
Mount volume to /app
Logs now stored on host
Delete & recreate container
Logs are still there

This is the foundation of persistent data in containers.
HOW THIS MAPS TO KUBERNETES (very important)
Docker Volume → Kubernetes PV (Persistent Volume)
 -v appdata:/app → Kubernetes PVC (Persistent Volume Claim)
Kubernetes YAML equivalent:
volumeMounts:
  - name: log-storage
    mountPath: /app

volumes:
  - name: log-storage
    persistentVolumeClaim:
      claimName: log-pvc

This is EXACTLY how real applications handle:
logs


uploads


DB storage


config files
