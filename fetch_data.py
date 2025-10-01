import requests

headers = {"user-agent": "TheDrawingCoder-Gamer/botcmc_script_importer/0.0.1", "accept": "*/*" }


def download(url, dst):
    with requests.get(url, headers=headers) as req:
        req.raise_for_status()
        with open(dst, "w") as f:
            f.write(req.text)
# I think its ok to fetch these files - _I_ am not distributing them, so :shrug:
def download_all():
    download("https://script.bloodontheclocktower.com/data/roles.json", "data/roles.json")
    download("https://script.bloodontheclocktower.com/data/jinx.json", "data/jinx.json")
    download("https://script.bloodontheclocktower.com/data/nightsheet.json", "data/nightsheet.json")
    download("https://script.bloodontheclocktower.com/data/tether.json", "data/tether.json")
    download("https://script.bloodontheclocktower.com/data/game-characters-restrictions.json", "data/game-characters-restrictions.json")

if __name__ == "__main__":
    download_all()