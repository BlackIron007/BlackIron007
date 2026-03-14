import json
import os

CURRENT = "data/repos.json"
SNAPSHOT = "data/repo_snapshot.json"

def repos_changed():

    with open(CURRENT) as f:
        repos = json.load(f)

    repo_names = sorted([r["name"] for r in repos])

    if not os.path.exists(SNAPSHOT):
        save_snapshot(repo_names)
        return True

    with open(SNAPSHOT) as f:
        old = json.load(f)

    if old != repo_names:
        save_snapshot(repo_names)
        return True

    return False

def save_snapshot(repo_names):

    with open(SNAPSHOT, "w") as f:
        json.dump(repo_names, f, indent=2)