import json
import math
import random
from PIL import Image, ImageDraw

WIDTH = 800
HEIGHT = 800
CENTER = (WIDTH // 2, HEIGHT // 2)
UNIVERSE_SCALE = 0.8
DOMAIN_COLORS = {
    "Artificial Intelligence": (155, 89, 182),      
    "Machine Learning": (142, 68, 173),             
    "Computer Vision": (230, 126, 34),              
    "Full Stack Development": (26, 188, 156),      
    "Web Development": (52, 152, 219),             
    "DevOps / Automation": (46, 204, 113)           
}
INPUT_FILE = "data/planet_layout.json"
COMMITS_FILE = "data/commit_counts.json"
CLUSTERS_FILE = "data/repo_clusters.json"
OUTPUT_FILE = "assets/universe_frame.png"

def load_planets():
    with open(INPUT_FILE) as f:
        return json.load(f)

def load_commit_counts():

    with open(COMMITS_FILE) as f:
        return json.load(f)


def load_clusters():

    with open(CLUSTERS_FILE) as f:
        return json.load(f)["mapping"]

def draw_starfield(draw):

    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        r = random.randint(1,2)

        draw.ellipse((x-r,y-r,x+r,y+r), fill=(220, 220, 220))

def draw_sun(draw):

    for r in range(90, 30, -6):

        glow = int(200 * (r / 90))

        draw.ellipse(
            (
                CENTER[0]-r,
                CENTER[1]-r,
                CENTER[0]+r,
                CENTER[1]+r
            ),
            fill=(255, 200, glow)
        )

def draw_orbits(draw, planets):

    for p in planets:

        r = p["orbit_radius"] * UNIVERSE_SCALE

        draw.ellipse(
            (
                CENTER[0]-r,
                CENTER[1]-r,
                CENTER[0]+r,
                CENTER[1]+r
            ),
            outline=(80,80,80)
        )

def draw_planets(draw, planets):

    commit_counts = load_commit_counts()
    clusters = load_clusters()

    if not commit_counts:
        max_commits = 1
    else:
        max_commits = max(commit_counts.values()) if commit_counts.values() else 1
    if max_commits == 0:
        max_commits = 1

    for p in planets:

        r = p["orbit_radius"] * UNIVERSE_SCALE
        angle = p["angle"]

        x = CENTER[0] + r * math.cos(angle)
        y = CENTER[1] + r * math.sin(angle)

        size = 10 + math.sqrt(commit_counts.get(p["name"], 0)) * 2

        domain = clusters.get(p["name"])
        color = DOMAIN_COLORS.get(domain, (200,200,200))

        draw.ellipse(
        (
        x-size-4,
        y-size-4,
        x+size+4,
        y+size+4
        ),
        fill=(80,80,80)
        )

        draw.ellipse(
        (
        x-size,
        y-size,
        x+size,
        y+size
        ),
        fill=color
        )

        dx = x - CENTER[0]
        dy = y - CENTER[1]

        if r == 0:
            continue

        label_offset = 22
        label_x = x + (dx / r) * label_offset
        label_y = y + (dy / r) * label_offset

        anchor = ("l" if dx > 0 else "r") + "m"

        draw.text(
            (label_x, label_y), p["name"], fill=(255, 255, 255), anchor=anchor
        )

def render():

    img = Image.new("RGB",(WIDTH,HEIGHT),(0,0,0))
    draw = ImageDraw.Draw(img)

    planets = load_planets()

    draw_starfield(draw)
    draw_orbits(draw, planets)
    draw_sun(draw)
    draw_planets(draw, planets)

    img.save(OUTPUT_FILE)

    print("Universe frame generated")

if __name__ == "__main__":
    render()