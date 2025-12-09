Scenario 2 was the **classic Docker networking problem** — the one that trips up almost every candidate in manager-level interviews.

Let’s restate it cleanly and then I’ll walk you through the exact hands-on steps.

---

# 🔥 **SCENARIO 2 — “App cannot connect to DB in Docker.”**

Your application container **can reach the database by IP**,
but **fails when using hostname** (e.g., `mydb`).

This is one of the most common microservices issues.

The reason:
**Docker’s internal DNS only works inside the same user-defined network.**

So you simulate a real production issue and fix it locally.

---

# 🎯 **GOAL OF THE EXERCISE**

1. Run a Postgres DB container.
2. Run a Python app container that tries to connect to it.
3. Observe that `localhost` fails.
4. Observe that hostname also fails if you’re not on the same Docker network.
5. Create a user-defined Docker network.
6. Reconnect containers → hostname starts working.

This builds the exact troubleshooting muscle managers test.

---

# ✅ **STEP-BY-STEP INSTRUCTIONS (copy-paste)**

Run these inside your `scenario2` folder.

---

# **STEP 1 — Create working directory**

```powershell
cd "D:\AZURE IS\DEVOPS\docker-all"
mkdir scenario2
cd scenario2
```

---

# **STEP 2 — Create `dbtest.py`**

```python
import psycopg2
print("Attempting connection...")

conn = psycopg2.connect(
    host="localhost",       # this will FAIL inside container
    port=5432,
    dbname="postgres",
    user="postgres",
    password="pass"
)

print("Connected successfully!")
```

---

# **STEP 3 — Create Dockerfile**

```dockerfile
FROM python:3.10

WORKDIR /app

COPY dbtest.py .
RUN pip install psycopg2-binary

CMD ["python", "dbtest.py"]
```

---

# **STEP 4 — Start Postgres container**

```powershell
docker run --name mydb -e POSTGRES_PASSWORD=pass -p 5432:5432 -d postgres
```

This runs PostgreSQL on your local Windows PC at port 5432.

---

# **STEP 5 — Build your test image**

```powershell
docker build -t dbtest .
```

---

# **STEP 6 — Run the test container (EXPECTED FAILURE)**

```powershell
docker run dbtest
```

Inside the container, `localhost` = **the container itself**, not your PC → so connection fails.

**This simulates a real DevOps networking issue.**

---

# ⚠️ **STEP 7 — Even hostname won’t work yet**

If you modify the host to `"mydb"` inside the container, it still fails because:

* container is NOT on the same Docker network
* built-in DNS is NOT active

This is where the fix begins.

---

# ⭐ **STEP 8 — Create a Docker network**

```powershell
docker network create mynet
```

---

# ⭐ **STEP 9 — Run Postgres inside this network**

```powershell
docker rm -f mydb

docker run --name mydb --network mynet -e POSTGRES_PASSWORD=pass -d postgres
```

Now its hostname inside the Docker network is literally **`mydb`**.

---

# ⭐ **STEP 10 — Update your Python code**

Modify `dbtest.py`:

```python
import psycopg2
print("Attempting connection...")

conn = psycopg2.connect(
    host="mydb",    # now hostname will work!
    port=5432,
    dbname="postgres",
    user="postgres",
    password="pass"
)

print("Connected successfully!")
```

Rebuild image:

```powershell
docker build -t dbtest .
```

---

# ⭐ **STEP 11 — Run app container inside the same network**

```powershell
docker run --network mynet dbtest
```

This time it will SUCCESSFULLY CONNECT.

🎉 Congratulations — you just solved one of the most frequent real-world container networking failures.

---

# 🧠 **WHY DOES THIS MATTER IN AN INTERVIEW?**

Because the exact scenario is used to evaluate if you understand:

* Docker DNS
* User-defined bridge networks
* Why localhost never works between containers
* Service discovery in container environments
* How microservices communicate
* How networking changes inside AKS

So your explanation becomes:

**“Containers don’t share localhost. To enable hostname resolution like `mydb`, both containers must be placed inside the same user-defined Docker network because that activates Docker’s embedded DNS. Once on the same network, the application can connect using `postgres`’s container name as hostname.”**

That’s a manager-level answer.

---