import requests
import re
import os
from urllib.request import urlopen

headers = {"user-agent": "TheDrawingCoder-Gamer/botcmc_script_importer/0.0.1", "accept": "*/*" }

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download(url, dst):
    if url.startswith("data:"):
        with urlopen(url) as res:
            with open(dst, "wb") as f:
                f.write(res.read())
    else:
        with requests.get(url, headers=headers) as req:
            req.raise_for_status()

            with open(dst, "w") as f:
                f.write(req.text)

def download_all():
    ensure_dir("data")
    
    download("https://release.botc.app/resources/data/roles.json", "data/roles.json")
    download("https://release.botc.app/resources/data/jinxes.json", "data/jinx.json")
    download("https://release.botc.app/resources/data/nightsheet.json", "data/nightsheet.json")


if __name__ == "__main__":
    download_all()
