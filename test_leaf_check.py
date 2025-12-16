import glob
from app import is_leaf_image

# find a sample image in the dataset
imgs = glob.glob('**/*.jpg', recursive=True)
if not imgs:
    imgs = glob.glob('**/*.png', recursive=True)
if not imgs:
    print('No images found to test.')
else:
    sample = imgs[0]
    print('Testing image:', sample)
    print('Is leaf image?', is_leaf_image(sample))
