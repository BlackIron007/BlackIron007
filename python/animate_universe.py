import json
import math
import random
from PIL import Image, ImageDraw, ImageFont

CENTER = (400, 400)
WIDTH = 800
HEIGHT = 800
UNIVERSE_SCALE = 0.8

FRAMES = 240

COMMITS_FILE = "data/commit_counts.json"
CLUSTERS_FILE = "data/repo_clusters.json"
LAYOUT_FILE = "data/planet_layout.json"

OUTPUT = "assets/universe.gif"

DOMAIN_COLORS = {
    "Artificial Intelligence": (155, 89, 182),
    "Machine Learning": (142, 68, 173),
    "Computer Vision": (230, 126, 34),
    "Full Stack Development": (26, 188, 156),
    "Web Development": (52, 152, 219),
    "DevOps / Automation": (46, 204, 113)
}


def load_json(path):
    with open(path) as f:
        return json.load(f)

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


def create_frame(layout, commit_counts, clusters, frame):

    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(img)
    
    random.seed(0)
    draw_starfield(draw)

    base_speed = (2 * math.pi) / FRAMES

    # Draw orbits first
    for p in layout:
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

    draw_sun(draw)

    # Then draw planets so they appear on top of orbits
    for p in layout:
        r = p["orbit_radius"] * UNIVERSE_SCALE
        base_angle = p["angle"]

        # All planets rotate at the same angular speed for a perfect, continuous loop
        speed = base_speed
        angle = base_angle + frame * speed

        x = CENTER[0] + r * math.cos(angle)
        y = CENTER[1] + r * math.sin(angle)
        commits = commit_counts.get(p["name"], 0)

        size = 10 + math.sqrt(commits) * 2

        domain = clusters.get(p["name"])

        color = DOMAIN_COLORS.get(domain, (200,200,200))

        # Draw border
        draw.ellipse(
            (x-size-4, y-size-4, x+size+4, y+size+4),
            fill=(80,80,80)
        )
        # Draw planet
        draw.ellipse(
            (x-size, y-size, x+size, y+size),
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

        draw.text((label_x, label_y), p["name"], fill=(255, 255, 255), anchor=anchor)

    return img


def main():

    layout = load_json(LAYOUT_FILE)

    commit_counts = load_json(COMMITS_FILE)

    clusters = load_json(CLUSTERS_FILE)["mapping"]

    frames = []

    for frame in range(FRAMES):

        img = create_frame(layout, commit_counts, clusters, frame)

        frames.append(img)

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0
    )

    print("Universe GIF generated")


if __name__ == "__main__":
    main()