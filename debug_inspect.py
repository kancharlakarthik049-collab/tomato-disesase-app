import os
import numpy as np
from PIL import Image
import tensorflow as tf

MODEL_PATH = 'models/tomato_model.h5'
IMG = 'static/uploads/debug/IMG-20251217-WA0007.jpg'

print('MODEL_PATH exists:', os.path.exists(MODEL_PATH))
print('IMG exists:', os.path.exists(IMG))

m = tf.keras.models.load_model(MODEL_PATH)
print('Model input shape:', m.input_shape)

img = Image.open(IMG).convert('RGB').resize((224,224))
arr = np.array(img).astype('float32')/255.0
arr = np.expand_dims(arr, axis=0)
print('Input array shape:', arr.shape)

preds = m.predict(arr)[0]
print('Predictions length:', len(preds))
for i,p in enumerate(preds):
    print(i, p)
print('argmax:', np.argmax(preds))
print('max:', np.max(preds))
