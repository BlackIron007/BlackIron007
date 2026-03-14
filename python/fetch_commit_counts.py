import json
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "BlackIron007"

INPUT = "data/repos.json"
OUTPUT = "data/commit_counts.json"

def get_commit_count(repo):

    url = f"https://api.github.com/repos/{USERNAME}/{repo}/commits"

    headers = {
        "Authorization": f"token {TOKEN}"
    }

    params = {"per_page": 1}

    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 409:
        return 0

    r.raise_for_status()

    if not r.json():
        return 0

    if "Link" in r.headers:

        link = r.headers["Link"]

        if 'rel="last"' in link:
            match = re.search(r'page=(\d+)>; rel="last"', link)
            if match:
                return int(match.group(1))

    return 1

def main():

    with open(INPUT) as f:
        repos = json.load(f)

    results = {}

    for repo in repos:

        name = repo["name"]

        count = get_commit_count(name)

        results[name] = count

        print(name, count)

    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()