import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

DEBUG_DIR = 'static/uploads/debug'
TARGET = 'IMG-20251217-WA0007.jpg'
IMG_PATH = os.path.join(DEBUG_DIR, TARGET)
OUT_PATH = os.path.join(DEBUG_DIR, f'crops_{TARGET}.png')

if not os.path.exists(IMG_PATH):
    print('Target image not found:', IMG_PATH)
    raise SystemExit(1)

img = Image.open(IMG_PATH).convert('RGB')
w_img, h_img = img.size
hsv = img.convert('HSV')
arr = np.array(hsv)
h = arr[:, :, 0]
s = arr[:, :, 1]
v = arr[:, :, 2]

# Heuristic: dark colored pixels within reasonably saturated regions
median_v = np.median(v)
V_THRESH = int(median_v * 0.6)
S_MIN = 40
mask_dark = (v < V_THRESH) & (s >= S_MIN)

# Sliding window scoring
win_w, win_h = 96, 96
stride = 48
scores = []
for y in range(0, max(1, h_img - win_h + 1), stride):
    for x in range(0, max(1, w_img - win_w + 1), stride):
        win = mask_dark[y:y+win_h, x:x+win_w]
        score = float(np.count_nonzero(win)) / (win_w * win_h)
        if score > 0:
            scores.append((score, x, y))

# If no dark spots found, fallback to green-mask areas
if not scores:
    GREEN_H_MIN = 25
    GREEN_H_MAX = 100
    mask_green = (h >= GREEN_H_MIN) & (h <= GREEN_H_MAX) & (s >= S_MIN)
    # compute boxes around green connected regions via coarse grid scoring
    for y in range(0, max(1, h_img - win_h + 1), stride):
        for x in range(0, max(1, w_img - win_w + 1), stride):
            win = mask_green[y:y+win_h, x:x+win_w]
            score = float(np.count_nonzero(win)) / (win_w * win_h)
            if score > 0.01:
                scores.append((score, x, y))

if not scores:
    print('No candidate regions found.')
    # still save original as out
    img.save(OUT_PATH)
    print('Saved', OUT_PATH)
    raise SystemExit(0)

# select top non-overlapping boxes (IoU < 0.3)
scores.sort(reverse=True, key=lambda t: t[0])
selected = []
for score, x, y in scores:
    box = (x, y, x+win_w, y+win_h)
    keep = True
    for _, bx in selected:
        # compute IoU
        x1 = max(box[0], bx[0])
        y1 = max(box[1], bx[1])
        x2 = min(box[2], bx[2])
        y2 = min(box[3], bx[3])
        inter = max(0, x2-x1) * max(0, y2-y1)
        area = (box[2]-box[0]) * (box[3]-box[1])
        area_b = (bx[2]-bx[0]) * (bx[3]-bx[1])
        union = area + area_b - inter
        iou = inter/union if union>0 else 0
        if iou > 0.3:
            keep = False
            break
    if keep:
        selected.append((score, box))
    if len(selected) >= 4:
        break

# draw boxes
out = img.copy().convert('RGBA')
draw = ImageDraw.Draw(out)
try:
    font = ImageFont.truetype('arial.ttf', 16)
except Exception:
    font = ImageFont.load_default()

for i, (score, box) in enumerate(selected):
    x1,y1,x2,y2 = box
    # outline
    for t in range(3):
        draw.rectangle([x1-t,y1-t,x2+t,y2+t], outline=(255,0,0,200))
    label = f'{i+1}: {score:.3f}'
    try:
        text_w, text_h = draw.textsize(label, font=font)
    except Exception:
        # fallback
        text_w = len(label) * 8
        text_h = 14
    draw.rectangle([x1, max(0,y1-text_h-6), x1+text_w+6, max(0,y1)], fill=(255,0,0,180))
    draw.text((x1+3, max(0,y1-text_h-4)), label, fill=(255,255,255,255), font=font)

out.save(OUT_PATH)
print('Saved crops image to', OUT_PATH)
