import requests
from bs4 import BeautifulSoup
import time
import os

BASE = "https://fastapi.tiangolo.com"

PAGES = [
    "/", "/tutorial/", "/tutorial/first-steps/", "/tutorial/path-params/",
    "/tutorial/query-params/", "/tutorial/body/", "/tutorial/response-model/",
    "/tutorial/extra-models/", "/tutorial/response-status-code/",
    "/tutorial/form-data/", "/tutorial/request-files/",
    "/tutorial/handling-errors/", "/tutorial/path-operation-configuration/",
    "/tutorial/body-updates/", "/tutorial/dependencies/",
    "/tutorial/dependencies/classes-as-dependencies/",
    "/tutorial/dependencies/sub-dependencies/",
    "/tutorial/dependencies/dependencies-with-yield/",
    "/tutorial/security/", "/tutorial/security/oauth2-jwt/",
    "/tutorial/middleware/", "/tutorial/cors/",
    "/tutorial/bigger-applications/", "/tutorial/background-tasks/",
    "/tutorial/testing/", "/tutorial/debugging/",
    "/deployment/", "/deployment/docker/", "/deployment/https/",
    "/advanced/", "/advanced/response-directly/",
    "/advanced/custom-response/", "/advanced/websockets/",
    "/advanced/events/", "/advanced/middleware/",
]

os.makedirs("corpus", exist_ok=True)

for path in PAGES:
    url = BASE + path
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        article = soup.find("article") or soup.find("main")
        if article:
            text = article.get_text(separator="\n").strip()
            if len(text) > 100:
                fname = path.replace("/", "_").strip("_") or "index"
                with open(f"corpus/{fname}.txt", "w") as f:
                    f.write(text)
                print(f"saved: {fname} ({len(text.split())} words)")
    except Exception as e:
        print(f"failed: {path} — {e}")
    time.sleep(0.8)

print("done")
