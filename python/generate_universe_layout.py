import json
import hashlib
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

    repo_count = len(repos)
    if not repo_count:
        return []

    planets_per_orbit = int(np.ceil(np.sqrt(repo_count)))
    base_orbit = 140
    orbit_spacing = 70

    sorted_repos = sorted(repos, key=lambda r: r["name"])

    for i, repo in enumerate(sorted_repos):

        orbit_index = i // planets_per_orbit
        planet_index_on_orbit = i % planets_per_orbit

        orbit = base_orbit + orbit_index * orbit_spacing

        angle_on_orbit = (planet_index_on_orbit / planets_per_orbit) * (2 * np.pi)

        orbit_angle_offset = (orbit_index % 2) * (np.pi / planets_per_orbit)

        hash_object = hashlib.md5(repo["name"].encode('utf-8'))
        hash_digest = hash_object.hexdigest()
        hash_int = int(hash_digest, 16)

        jitter_range = np.pi / 18
        angle_jitter = ((hash_int % 1000) / 1000.0) * (2 * jitter_range) - jitter_range

        angle = angle_on_orbit + orbit_angle_offset + angle_jitter

        planet = {
            "name": repo["name"],
            "orbit_radius": orbit,
            "planet_size": 12 + (i % 4) * 3,
            "angle": angle,
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