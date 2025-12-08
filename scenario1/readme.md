Nice — let’s do Scenario 1 end-to-end on your PC. You’ll create a tiny FastAPI app, build a deliberately **bad** image, measure it, 
then make an **optimized** multi-stage image and compare sizes.

Everything fits in one folder `D:\AZURE IS\DEVOPS\docker-all\scenario1`. Run commands from there.

# 1) Create working folder and files

```powershell
# change to your working dir
cd "D:\AZURE IS\DEVOPS\docker-all"

# make scenario folder
mkdir scenario1
cd scenario1
```

Create three files: `main.py`, `requirements.txt`, and a bad `Dockerfile`.

`main.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"hello": "world"}
```

`requirements.txt`

```
fastapi
uvicorn[standard]
```

`Dockerfile.bad` (intentionally naive / heavy)

```
FROM python:3.10

WORKDIR /app

# Copy everything early (bad: includes dev files, invalidates cache)
COPY . .

# Install dependencies (this creates a big layer)
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `.dockerignore` (we'll use it for the good build too)

```
__pycache__
*.pyc
.env
.git
.gitignore
```

# 2) Build the bad image and inspect size

```powershell
# Build bad image
docker build -f Dockerfile.bad -t myfastapi:bad .

# List image sizes (PowerShell friendly formatting)
docker images --format "{{.Repository}}:{{.Tag}} - {{.Size}}"
```

Note the bad image size (likely several hundred MB to ~1GB depending on base image layers).

# 3) Inspect the image history to see where space is used

```powershell
docker history myfastapi:bad --no-trunc
```

Look for large layers (the `RUN pip install` layer is usually the largest).

# 4) Create an optimized multi-stage Dockerfile

Create `Dockerfile` with this content:

```
# Stage 1: build dependencies (builder)
FROM python:3.10-slim as builder
WORKDIR /app

# Copy only requirements first to leverage cache
COPY requirements.txt .

# Install dependencies into a virtual location
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: runtime image
FROM python:3.10-slim
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy only application code (now this layer changes often — placed after deps)
COPY main.py .

ENV PATH=/usr/local/bin:$PATH

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Why this is better (short): install dependencies in a separate stage and only copy required runtime files into a small `slim` base. Also copy `requirements.txt` first so dependency layer is cached unless requirements change.

# 5) Build the optimized image

```powershell
docker build -t myfastapi:good .
docker images --format "{{.Repository}}:{{.Tag}} - {{.Size}}"
```

# 6) Compare sizes (bad vs good)

You should see `myfastapi:good` is much smaller than `myfastapi:bad`. Example commands:

```powershell
docker images --filter=reference="myfastapi:*" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
```

# 7) Run both images (optional) to verify behavior

```powershell
# run good image on port 8000
docker run -d --name fast-good -p 8000:8000 myfastapi:good

# open browser: http://localhost:8000
# verify JSON {"hello":"world"}

# stop & remove
docker rm -f fast-good
```

# 8) Clean up dangling layers & measure reclaimed space

Before prune, check Docker disk usage:

```powershell
docker system df
```

Prune unused stuff (careful: this removes images/containers not in use):

```powershell
docker system prune -af
```

Check disk usage again:

```powershell
docker system df
```

# 9) Extra optimizations you can try (iterate & measure)

* Use `python:3.10-slim-buster` or `distroless` runtime image to reduce OS footprint.
* Use `--no-cache-dir` in `pip install` (already used).
* Use `pip install --only-binary=:all:` when possible to avoid building wheels.
* For compiled language builds, do real multi-stage: build in full SDK image, copy binary into `scratch` or minimal runtime.
* Minimize copied files with `.dockerignore` (node_modules, tests, docs, large assets).

# 10) Commands to show which layers are largest

```powershell
# show layers with sizes for the good image
docker history myfastapi:good --no-trunc
```

Look at the size column — you can iterate by changing Dockerfile ordering and re-building to see effect.

---

## Quick explanation you can say in interview

“We reduced image size by using a multi-stage build: install dependencies in a builder stage and copy only the runtime artifacts into a slim base. We also moved `COPY requirements.txt` before copying the source so the dependency layer is cached across builds. Finally, `.dockerignore` avoids copying unnecessary files into images. These changes dramatically reduce push/pull times and startup latency in AKS.”

---