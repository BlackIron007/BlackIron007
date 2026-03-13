import json
import math
from PIL import Image, ImageDraw

WIDTH = 800
HEIGHT = 800
CENTER = (WIDTH // 2, HEIGHT // 2)

INPUT_FILE = "data/planet_layout.json"
OUTPUT_FILE = "assets/universe_frame.png"

def load_planets():
    with open(INPUT_FILE) as f:
        return json.load(f)

def draw_starfield(draw):

    import random

    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        r = random.randint(1,2)

        draw.ellipse((x-r,y-r,x+r,y+r), fill="white")

def draw_sun(draw):

    r = 30

    draw.ellipse(
        (
            CENTER[0]-r,
            CENTER[1]-r,
            CENTER[0]+r,
            CENTER[1]+r
        ),
        fill=(255,200,0)
    )

def draw_orbits(draw, planets):

    for p in planets:

        r = p["orbit_radius"]

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

    for p in planets:

        r = p["orbit_radius"]
        angle = p["angle"]

        x = CENTER[0] + r * math.cos(angle)
        y = CENTER[1] + r * math.sin(angle)

        size = p["planet_size"]

        draw.ellipse(
            (
                x-size,
                y-size,
                x+size,
                y+size
            ),
            fill=p["color"]
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