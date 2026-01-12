import json
from collections import Counter

LOG = 'static/uploads/debug/debug_logs.jsonl'
CLASS_LABELS = [
    'Bacterial_spot', 'Early_blight', 'Late_blight',
    'Leaf_Mold', 'Septoria_leaf_spot', 'Spider_mites',
    'Target_Spot', 'Yellow_Leaf_Curl_Virus',
    'Mosaic_virus', 'Healthy'
]

entries = []
try:
    with open(LOG, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
except FileNotFoundError:
    print('No debug log found at', LOG)
    raise

print(f'Total debug entries: {len(entries)}\n')

agg_top = Counter()
uncount = 0
files = Counter()

for e in entries:
    fname = e.get('filename')
    files[fname] += 1
    raw = e.get('raw_predictions', [])
    if raw:
        # get top-3
        top = sorted(enumerate(raw), key=lambda x: x[1], reverse=True)[:3]
        top3 = [(CLASS_LABELS[idx], float(score)) for idx,score in top]
    else:
        top3 = []
    print('File:', fname)
    print(' Endpoint:', e.get('endpoint'))
    print(' Reported prediction:', e.get('prediction'), 'confidence:', e.get('confidence'))
    print(' Uncertain flag:', e.get('uncertain', False))
    print(' Top-3:')
    for label,score in top3:
        print('  -', label, f'{score:.4f}')
    print()
    if e.get('uncertain'):
        uncount += 1
    if top3:
        agg_top[top3[0][0]] += 1

print('Files seen and counts:')
for f,c in files.items():
    print('-', f, c)

print('\nTop reported top-1 labels count:')
for k,v in agg_top.most_common():
    print(f' - {k}: {v}')

print(f'\nUncertain entries: {uncount} / {len(entries)}')

# Suggestions
print('\nSuggestions:')
print('- If many entries are "Uncertain", consider lowering CONF_THRESH or collecting more labeled training images.')
print('- If specific wrong classes dominate (e.g., Early_blight predicted often), examine training label distribution and class mapping.')
print('- Inspect the images in static/uploads/debug/ to verify content and cropping.')
