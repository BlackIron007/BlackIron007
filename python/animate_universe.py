import json
import math
import random
from PIL import Image, ImageDraw, ImageFont

WIDTH = 700
HEIGHT = 700
CENTER = (WIDTH // 2, HEIGHT // 2)
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

def get_font(size=12):
    """Tries to load a system TrueType font, falling back to the default."""
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except IOError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            print("Warning: TrueType font not found. Labels may jitter.")
            return ImageFont.load_default()


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

def draw_orbits(draw, layout):
    for p in layout:
        r = p["orbit_radius"] * UNIVERSE_SCALE
        draw.ellipse(
            (CENTER[0]-r, CENTER[1]-r, CENTER[0]+r, CENTER[1]+r),
            outline=(80,80,80)
        )

def add_planets_to_frame(base_img, layout, commit_counts, clusters, frame, font):

    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    
    base_speed = (2 * math.pi) / FRAMES

    for p in layout:
        r = p["orbit_radius"] * UNIVERSE_SCALE
        base_angle = p["angle"]

        speed = base_speed
        angle = base_angle + frame * speed

        x = CENTER[0] + r * math.cos(angle)
        y = CENTER[1] + r * math.sin(angle)
        commits = commit_counts.get(p["name"], 0)

        size = 10 + math.sqrt(commits) * 2

        domain = clusters.get(p["name"])

        color = DOMAIN_COLORS.get(domain, (200,200,200))

        draw.ellipse(
            (x-size-4, y-size-4, x+size+4, y+size+4),
            fill=(80,80,80)
        )
        draw.ellipse(
            (x-size, y-size, x+size, y+size),
            fill=color
        )

        dx = x - CENTER[0]
        dy = y - CENTER[1]

        if r == 0:
            continue

        label_offset = 22
        attach_x = x + (dx / r) * label_offset
        attach_y = y + (dy / r) * label_offset

        text_width = draw.textlength(p["name"], font=font)
        
        cos_angle = math.cos(angle)
        
        progress = (cos_angle + 1) / 2.0
        
        x_offset = (1.0 - progress) * -text_width

        draw.text((attach_x + x_offset, attach_y), p["name"], fill=(255, 255, 255), anchor="lm", font=font)

    return img


def main():

    layout = load_json(LAYOUT_FILE)

    commit_counts = load_json(COMMITS_FILE)

    clusters = load_json(CLUSTERS_FILE)["mapping"]

    font = get_font()

    base_img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(base_img)
    
    random.seed(0)
    draw_starfield(draw)
    draw_orbits(draw, layout)
    draw_sun(draw)

    frames = []
    for frame in range(FRAMES):
        img = add_planets_to_frame(base_img, layout, commit_counts, clusters, frame, font)
        frames.append(img)

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0
    )

    print("Universe GIF generated successfully.")


if __name__ == "__main__":
    main()