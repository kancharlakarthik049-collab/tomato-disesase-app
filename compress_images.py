from PIL import Image
import os
import glob

root = 'static/uploads'
count=0
for ext in ('*.jpg','*.jpeg','*.png'):
    for path in glob.glob(os.path.join(root,'**',ext), recursive=True):
        if 'debug' in path.replace('\\','/').lower():
            continue
        try:
            img = Image.open(path)
            img = img.convert('RGB')
            img.thumbnail((1024,1024))
            img.save(path, quality=80, optimize=True)
            count+=1
        except Exception as e:
            print('skip', path, e)
print('Processed', count, 'images')
