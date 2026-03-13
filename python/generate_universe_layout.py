import json
import random
import numpy as np

INPUT_FILE = "data/repos.json"
OUTPUT_FILE = "data/planet_layout.json"

LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#2b7489",
    "HTML": "#e34c26",
    "Dockerfile": "#384d54",
    None: "#888888"
}

def load_repos():
    with open(INPUT_FILE) as f:
        return json.load(f)

def generate_layout(repos):

    layout = []

    base_orbit = 120
    orbit_spacing = 60

    for i, repo in enumerate(repos):

        orbit = base_orbit + i * orbit_spacing

        planet = {
            "name": repo["name"],
            "orbit_radius": orbit,
            "planet_size": 10 + repo["stars"] * 2,
            "angle": random.uniform(0, 2*np.pi),
            "color": LANGUAGE_COLORS.get(repo["language"], "#aaaaaa")
        }

        layout.append(planet)

    return layout

def save_layout(layout):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(layout, f, indent=2)

if __name__ == "__main__":

    repos = load_repos()

    layout = generate_layout(repos)

    save_layout(layout)

    print(f"Generated layout for {len(layout)} planets")