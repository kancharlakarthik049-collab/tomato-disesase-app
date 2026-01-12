import json
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

DEBUG_DIR = 'static/uploads/debug'
LOG = os.path.join(DEBUG_DIR, 'debug_logs.jsonl')
TARGET = 'IMG-20251217-WA0007.jpg'
OUT = os.path.join(DEBUG_DIR, f'annotated_{TARGET}.png')

# Read last matching log entry
entry = None
with open(LOG, 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('filename') == TARGET:
            entry = obj

if entry is None:
    print('No log entry found for', TARGET)
    raise SystemExit(1)

img_path = os.path.join(DEBUG_DIR, TARGET)
if not os.path.exists(img_path):
    print('Image not found:', img_path)
    raise SystemExit(1)

# Load image
img = Image.open(img_path).convert('RGB')
# Create mask based on HSV heuristic
hsv = img.convert('HSV')
arr = np.array(hsv)
h = arr[:, :, 0]
s = arr[:, :, 1]
v = arr[:, :, 2]
# thresholds approximated from app.py defaults
GREEN_H_MIN = 25
GREEN_H_MAX = 100
S_MIN = 40
V_MIN = 40
mask = (h >= GREEN_H_MIN) & (h <= GREEN_H_MAX) & (s >= S_MIN) & (v >= V_MIN)

# Create RGBA overlay
overlay = Image.new('RGBA', img.size, (0,0,0,0))
green_layer = Image.new('RGBA', img.size, (0,255,0,120))
mask_img = Image.fromarray((mask * 255).astype('uint8'))
overlay.paste(green_layer, mask=mask_img)

base = img.convert('RGBA')
combined = Image.alpha_composite(base, overlay)

# Draw top-3
draw = ImageDraw.Draw(combined)
try:
    font = ImageFont.truetype('arial.ttf', 18)
except Exception:
    font = ImageFont.load_default()

raw = entry.get('raw_predictions', [])
labels = [
    'Bacterial_spot', 'Early_blight', 'Late_blight',
    'Leaf_Mold', 'Septoria_leaf_spot', 'Spider_mites',
    'Target_Spot', 'Yellow_Leaf_Curl_Virus', 'Mosaic_virus', 'Healthy'
]
if raw:
    top = sorted(enumerate(raw), key=lambda x: x[1], reverse=True)[:3]
else:
    top = []

text_lines = [f"Reported: {entry.get('prediction')} ({entry.get('confidence')}%)", 'Top-3:']
for idx,score in top:
    text_lines.append(f"{labels[idx]}: {score:.4f}")

# background box
padding = 8
text = '\n'.join(text_lines)
# PIL older versions may not have multiline_textsize; compute via textsize per line
lines = text.split('\n')
line_sizes = []
for line in lines:
    try:
        sz = font.getsize(line)
    except Exception:
        # fallback conservative guess
        sz = (len(line)*8, 14)
    line_sizes.append(sz)

w = max(sz[0] for sz in line_sizes)
# approximate total height
h_text = sum(sz[1] for sz in line_sizes) + (len(lines)-1)*4
box_w = w + padding*2
box_h = h_text + padding*2
# semi-transparent black box
draw.rectangle([(10,10),(10+box_w,10+box_h)], fill=(0,0,0,180))
# text
draw.multiline_text((10+padding,10+padding), text, fill=(255,255,255,255), font=font)

combined.save(OUT)
print('Annotated image saved to', OUT)
