"""Generates the offline demo images in app/seed_assets/ (simple illustrations, not photos).

Run from backend/:  .venv/bin/python scripts/generate_demo_images.py
The generated JPEGs are committed; you only need to re-run this to change them.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parents[1] / "app" / "seed_assets"
S = 2  # supersample factor for smooth edges
W, H = 800 * S, 600 * S


def font(size: int):
    for path in ("/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(path, size * S)
        except OSError:
            pass
    return ImageFont.load_default(size * S)


def sc(v):  # scale helper: authoring coordinates are in an 800x600 space
    if isinstance(v, (list, tuple)):
        return [tuple(y * S for y in x) if isinstance(x, (list, tuple)) else x * S for x in v]
    return v * S


def canvas():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(238 - 26 * t), int(242 - 24 * t), int(247 - 22 * t)))
    d.rectangle([0, int(H * 0.72), W, H], fill=(205, 196, 184))  # table
    return img


def shadow(img, box, blur=14, alpha=110):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(sc(box), fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur * S))
    img.paste(layer, (0, 0), layer)


def rr(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(sc(box), radius=r * S, fill=fill, outline=outline, width=width * S)


def gradient_rr(img, box, r, top, bottom, vertical=True):
    x0, y0, x1, y1 = [int(v * S) for v in box]
    g = Image.new("RGB", (x1 - x0, y1 - y0))
    gd = ImageDraw.Draw(g)
    n = (y1 - y0) if vertical else (x1 - x0)
    for i in range(n):
        t = i / max(n - 1, 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        gd.line([(0, i), (g.width, i)] if vertical else [(i, 0), (i, g.height)], fill=c)
    mask = Image.new("L", g.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, g.width - 1, g.height - 1], radius=r * S, fill=255)
    img.paste(g, (x0, y0), mask)


def text(d, xy, s, size, fill, anchor="mm"):
    d.text(sc(xy), s, font=font(size), fill=fill, anchor=anchor)


def save(img, name):
    img.resize((800, 600), Image.LANCZOS).save(OUT / f"{name}.jpg", "JPEG", quality=86, optimize=True)


def laptop():
    img = canvas(); shadow(img, [120, 420, 680, 470])
    d = ImageDraw.Draw(img)
    rr(d, [180, 130, 620, 390], 14, (34, 34, 38))
    gradient_rr(img, [198, 146, 602, 372], 6, (18, 70, 130), (70, 150, 210))
    d.ellipse(sc([390, 152, 410, 166]), fill=(70, 70, 76))
    d.polygon(sc([(120, 400), (680, 400), (730, 440), (70, 440)]), fill=(52, 52, 58))
    d.polygon(sc([(120, 400), (680, 400), (690, 410), (110, 410)]), fill=(78, 78, 86))
    for row in range(3):
        for col in range(14):
            x = 150 + col * 37 + row * 6
            rr(d, [x, 414 + row * 7, x + 30, 419 + row * 7], 1, (30, 30, 34))
    rr(d, [350, 428, 450, 436], 3, (40, 40, 46))
    d.ellipse(sc([392, 372, 408, 388]), fill=(150, 150, 158))  # logo disc (generic)
    # scratch near the logo (matches the demo's private detail)
    d.line(sc([(420, 376), (436, 384)]), fill=(200, 200, 205), width=S)
    save(img, "laptop")


def bottle():
    img = canvas(); shadow(img, [290, 440, 510, 480])
    d = ImageDraw.Draw(img)
    gradient_rr(img, [300, 150, 500, 460], 40, (30, 100, 185), (20, 70, 140), vertical=False)
    gradient_rr(img, [355, 80, 445, 170], 12, (34, 100, 175), (24, 76, 140), vertical=False)
    rr(d, [345, 40, 455, 92], 10, (45, 45, 50))
    for x in range(352, 452, 12):
        d.line(sc([(x, 44), (x, 88)]), fill=(70, 70, 76), width=S)
    rr(d, [300, 250, 500, 330], 0, (200, 205, 212))
    text(d, (400, 290), "STEEL", 30, (40, 60, 90))
    rr(d, [322, 175, 340, 440], 8, (120, 175, 235))  # highlight
    d.ellipse(sc([470, 230, 490, 250]), fill=(18, 62, 120))  # dent
    d.ellipse(sc([376, 436, 424, 446]), fill=(20, 60, 110))
    save(img, "bottle")


def watch():
    img = canvas(); shadow(img, [260, 450, 540, 490])
    d = ImageDraw.Draw(img)
    for y0, y1 in ((40, 200), (400, 560)):
        for i, y in enumerate(range(y0, y1, 20)):
            rr(d, [345, y, 455, y + 17], 4, (185, 190, 198), (130, 135, 145), 1)
    d.ellipse(sc([255, 175, 545, 465]), fill=(170, 175, 185), outline=(120, 125, 135), width=4 * S)
    d.ellipse(sc([280, 200, 520, 440]), fill=(28, 30, 34))
    rr(d, [305, 255, 495, 385], 10, (150, 170, 140))
    text(d, (400, 305), "12:45", 56, (34, 44, 34))
    text(d, (400, 355), "MON 30", 26, (34, 44, 34))
    d.line(sc([(470, 215), (500, 255)]), fill=(255, 255, 255), width=S * 2)  # crack
    save(img, "watch")


def idcard():
    img = canvas(); shadow(img, [150, 440, 650, 480])
    d = ImageDraw.Draw(img)
    rr(d, [130, 110, 670, 470], 26, (235, 240, 245), (185, 195, 205), 3)  # plastic holder
    rr(d, [365, 92, 435, 120], 10, (200, 205, 212))
    rr(d, [160, 150, 640, 450], 14, (255, 255, 255), (210, 214, 220), 2)
    rr(d, [160, 150, 640, 210], 14, (30, 64, 140))
    text(d, (400, 180), "CAMPUS COLLEGE", 34, (255, 255, 255))
    rr(d, [190, 240, 320, 400], 8, (205, 212, 222))
    d.ellipse(sc([225, 255, 285, 315]), fill=(150, 160, 175))
    d.pieslice(sc([205, 315, 305, 420]), 180, 360, fill=(150, 160, 175))
    for i, (w, c) in enumerate(((220, (60, 64, 72)), (180, (130, 136, 146)), (200, (130, 136, 146)))):
        rr(d, [350, 250 + i * 40, 350 + w, 268 + i * 40], 4, c)
    text(d, (470, 420), "STUDENT", 24, (30, 64, 140))
    save(img, "idcard")


def textbook():
    img = canvas(); shadow(img, [200, 470, 600, 505])
    d = ImageDraw.Draw(img)
    rr(d, [250, 70, 570, 490], 6, (245, 238, 215))
    d.rectangle(sc([262, 78, 575, 484]), fill=(250, 246, 228))
    gradient_rr(img, [230, 60, 550, 480], 6, (178, 34, 44), (140, 22, 34), vertical=False)
    d.rectangle(sc([230, 60, 252, 480]), fill=(112, 16, 26))
    rr(d, [270, 110, 530, 250], 4, (236, 224, 200))
    text(d, (400, 150), "UNIVERSITY", 30, (120, 20, 28))
    text(d, (400, 200), "PHYSICS", 44, (120, 20, 28))
    d.ellipse(sc([345, 300, 455, 410]), outline=(236, 224, 200), width=4 * S)
    d.ellipse(sc([390, 345, 410, 365]), fill=(236, 224, 200))
    d.rectangle(sc([515, 62, 532, 100]), fill=(250, 210, 70))  # highlighter tab
    save(img, "textbook")


def umbrella():
    img = canvas(); shadow(img, [250, 470, 550, 500], alpha=70)
    d = ImageDraw.Draw(img)
    d.pieslice(sc([100, 60, 700, 520]), 180, 360, fill=(200, 35, 45))
    for i in range(8):
        x = 100 + i * 75 + 37
        d.ellipse(sc([x - 38, 255, x + 38, 300]), fill=(240, 240, 244))  # scallop gaps
    d.pieslice(sc([100, 60, 700, 520]), 180, 360, fill=None, outline=(150, 20, 30), width=3 * S)
    for ang in (-150, -120, -90, -60, -30):
        import math
        x = 400 + 300 * math.cos(math.radians(ang)); y = 290 + 230 * math.sin(math.radians(ang))
        d.line(sc([(400, 70), (x, y)]), fill=(140, 20, 28), width=2 * S)
    d.line(sc([(400, 290), (400, 440)]), fill=(110, 75, 45), width=10 * S)
    d.arc(sc([400, 400, 470, 480]), 0, 180, fill=(110, 75, 45), width=10 * S)
    rr(d, [394, 440, 406, 470], 3, (250, 250, 250))  # tag
    d.ellipse(sc([392, 58, 408, 74]), fill=(90, 60, 40))
    save(img, "umbrella")


def _key(img, angle, color, teeth, pivot=(325, 205)):
    layer = Image.new("RGBA", (360 * S, 120 * S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse(sc([10, 20, 90, 100]), fill=color, outline=(110, 112, 120), width=3 * S)
    ld.ellipse(sc([35, 45, 65, 75]), fill=(0, 0, 0, 0))
    ld.rectangle(sc([85, 50, 340, 70]), fill=color, outline=(110, 112, 120), width=2 * S)
    for x in teeth:
        ld.rectangle(sc([x, 70, x + 14, 92]), fill=color, outline=(110, 112, 120), width=2 * S)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    # head centre is (50, 60) in the unrotated layer; rotation is about the layer centre (180, 60)
    th = math.radians(angle)
    vx = (50 - 180) * S
    hx, hy = vx * math.cos(th), -vx * math.sin(th)
    px, py = pivot[0] * S, pivot[1] * S
    img.paste(layer, (int(px - hx - layer.width / 2), int(py - hy - layer.height / 2)), layer)


def keys():
    img = canvas(); shadow(img, [200, 470, 600, 500], alpha=70)
    _key(img, -125, (190, 194, 202), (220, 255, 290))
    _key(img, -60, (176, 180, 190), (230, 270))
    _key(img, -92, (208, 212, 220), (215, 250, 300))
    d = ImageDraw.Draw(img)
    d.ellipse(sc([255, 130, 395, 270]), outline=(150, 155, 165), width=8 * S)
    d.line(sc([(385, 225), (440, 222)]), fill=(150, 155, 165), width=5 * S)
    rr(d, [405, 215, 485, 340], 16, (40, 110, 200))
    text(d, (445, 278), "FC", 34, (255, 255, 255))
    d.ellipse(sc([435, 224, 455, 244]), fill=(235, 240, 250))
    save(img, "keys")


def wallet():
    img = canvas(); shadow(img, [150, 400, 650, 450])
    d = ImageDraw.Draw(img)
    rr(d, [250, 110, 410, 230], 8, (220, 70, 70))  # card peeking out
    rr(d, [265, 130, 330, 150], 3, (250, 220, 220))
    gradient_rr(img, [160, 170, 640, 430], 28, (52, 48, 48), (22, 20, 20))
    gradient_rr(img, [160, 170, 640, 290], 28, (64, 58, 58), (34, 31, 31))
    rr(d, [178, 188, 622, 412], 18, None, (98, 88, 78), 2)  # stitching
    d.rounded_rectangle(sc([178, 188, 622, 412]), radius=18 * S, outline=(98, 88, 78), width=2 * S)
    rr(d, [375, 268, 425, 312], 10, (180, 160, 110))  # clasp
    d.ellipse(sc([392, 282, 408, 298]), fill=(120, 105, 70))
    d.arc(sc([165, 175, 300, 260]), 200, 250, fill=(110, 105, 105), width=3 * S)  # highlight
    save(img, "wallet")


def calculator():
    img = canvas(); shadow(img, [220, 480, 580, 510])
    d = ImageDraw.Draw(img)
    gradient_rr(img, [230, 30, 570, 500], 30, (58, 60, 66), (36, 38, 42))
    rr(d, [255, 55, 545, 145], 8, (160, 182, 150), (20, 20, 20), 3)
    text(d, (525, 100), "3.14159", 46, (30, 42, 30), "rm")
    rr(d, [255, 158, 350, 178], 4, (90, 94, 100))
    cols = [(92, 96, 104)] * 5
    for r in range(3):
        for c in range(5):
            rr(d, [258 + c * 57, 190 + r * 36, 258 + c * 57 + 48, 190 + r * 36 + 26], 6, cols[c])
    for r in range(4):
        for c in range(5):
            x, y = 258 + c * 57, 312 + r * 45
            fill = (214, 70, 70) if (r == 0 and c >= 3) else (232, 234, 238) if c < 3 and r > 0 else (120, 124, 132)
            rr(d, [x, y, x + 48, y + 34], 7, fill)
            if c < 3 and r > 0:
                text(d, (x + 24, y + 17), str(3 * (3 - r) + c + 1 if r < 4 else 0), 20, (40, 42, 48))
    save(img, "calculator")


def backpack():
    img = canvas(); shadow(img, [190, 460, 610, 500])
    d = ImageDraw.Draw(img)
    d.arc(sc([330, 40, 470, 140]), 180, 360, fill=(20, 70, 44), width=12 * S)  # handle
    rr(d, [200, 240, 240, 410], 14, (24, 84, 52)); rr(d, [560, 240, 600, 410], 14, (24, 84, 52))  # side pockets
    gradient_rr(img, [230, 90, 570, 480], 70, (40, 130, 84), (26, 92, 58))
    d.line(sc([(260, 185), (540, 185)]), fill=(18, 64, 40), width=4 * S)  # top zipper
    gradient_rr(img, [265, 290, 535, 440], 24, (30, 104, 66), (22, 78, 50))
    d.line(sc([(285, 312), (515, 312)]), fill=(200, 205, 200), width=3 * S)
    rr(d, [390, 304, 410, 330], 4, (220, 200, 90))  # zipper pull
    rr(d, [330, 340, 470, 400], 8, None, (16, 60, 38), 3)
    rr(d, [275, 110, 300, 290], 10, (20, 72, 46)); rr(d, [500, 110, 525, 290], 10, (20, 72, 46))  # straps
    save(img, "backpack")


def smartphone():
    img = canvas(); shadow(img, [260, 500, 540, 530], alpha=80)
    d = ImageDraw.Draw(img)
    rr(d, [270, 30, 530, 520], 40, (14, 14, 16), (60, 60, 66), 3)
    gradient_rr(img, [282, 44, 518, 506], 30, (74, 52, 160), (238, 130, 70))
    d.ellipse(sc([392, 56, 408, 72]), fill=(10, 10, 12))
    text(d, (400, 140), "12:45", 62, (255, 255, 255))
    text(d, (400, 188), "Tuesday, 30 September", 17, (240, 235, 250))
    palette = [(66, 133, 244), (52, 168, 83), (251, 188, 5), (234, 67, 53)] * 2
    for i, c in enumerate(palette):
        x, y = 310 + (i % 4) * 52, 330 + (i // 4) * 62
        rr(d, [x, y, x + 40, y + 40], 10, c)
    rr(d, [360, 472, 440, 478], 3, (245, 245, 250))
    save(img, "smartphone")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (laptop, bottle, watch, idcard, textbook, umbrella, keys, wallet, calculator, backpack, smartphone):
        fn()
    print("generated", sorted(p.name for p in OUT.glob("*.jpg")))
