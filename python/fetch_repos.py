import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = "BlackIron007"
TOKEN = os.getenv("GITHUB_TOKEN")

OUTPUT_FILE = "data/repos.json"

def fetch_repositories():

    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"token {TOKEN}"
    }

    params = {
        "per_page": 100
    }

    response = requests.get(url, headers=headers, params=params)

    repos = response.json()

    results = []

    for repo in repos:

        if repo["owner"]["login"] != USERNAME:
            continue

        if repo["name"] == USERNAME:
            continue

        results.append({
            "name": repo["name"],
            "language": repo["language"],
            "stars": repo["stargazers_count"],
            "updated_at": repo["updated_at"]
        })

    return results

def save_data(data):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":

    repos = fetch_repositories()

    save_data(repos)

    print(f"Fetched {len(repos)} repositories")