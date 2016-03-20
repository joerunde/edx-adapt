import requests
import time

while True:
    r = requests.get("http://cmustats.tk:9000/api/v1/misc/hitcheck/course/CMUSTAT101")
    print r.json()
    time.sleep(60)


