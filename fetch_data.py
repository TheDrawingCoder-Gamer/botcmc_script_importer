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

def make_shadow_map_regex(name: str):
    return re.compile(fr'mapShadow\(`/data/{name}\.json`,.\.encode\(await fetch\(new URL\(`(.+?)`')

def make_asset_regex(name: str):
    return re.compile(fr'`(/assets/{name}.*?\.json)`')

def try_find_json(js: str, name: str):
    asset_regex = make_asset_regex(name)
    result = asset_regex.search(js)
    if result != None:
        return f"https://script.bloodontheclocktower.com{result.group(1)}"
    else:
        shadow_regex = make_shadow_map_regex(name)
        result2 = shadow_regex.search(js)
        if result2 != None:
            return result2.group(1)
    
    raise RuntimeError(f"Failed to find JSON for {name}")

script_regex = re.compile(r'script type="module" crossorigin src="(.+)"')

def download_all():
    ensure_dir("data")
    js_url = None
    with requests.get("https://script.bloodontheclocktower.com/", headers=headers) as req:
        req.raise_for_status()
        js_url = script_regex.search(req.text)
        
    if js_url != None:
        with requests.get(f"https://script.bloodontheclocktower.com{js_url.group(1)}", headers=headers) as req:
            req.raise_for_status()
            js = req.text
           
            jinxes_url = try_find_json(js, "jinxes")
            roles_url = try_find_json(js, "roles")
            nightsheet_url = try_find_json(js, "nightsheet")
        
        download(nightsheet_url, "data/nightsheet.json")
        download(jinxes_url, "data/jinx.json")
        download(roles_url, "data/roles.json")


if __name__ == "__main__":
    download_all()