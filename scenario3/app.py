from time import sleep, time


while True:
    with open("app.log", "a") as f:
        f.write(f"Log entry at: {time()}\n")
    sleep(2)
