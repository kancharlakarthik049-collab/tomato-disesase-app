import os
import sys

MODEL_PATH = os.path.join('models', 'tomato_model.h5')
OUT_PATH = os.path.join('models', 'tomato_model.tflite')

if not os.path.exists(MODEL_PATH):
    print(f"Model file not found: {MODEL_PATH}")
    sys.exit(1)

try:
    import tensorflow as tf
    print('Loading Keras model...')
    model = tf.keras.models.load_model(MODEL_PATH)

    print('Converting to TFLite (float32)...')
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    with open(OUT_PATH, 'wb') as f:
        f.write(tflite_model)

    orig_size = os.path.getsize(MODEL_PATH)
    tflite_size = os.path.getsize(OUT_PATH)
    print(f'Wrote TFLite model to {OUT_PATH}')
    print(f'Original size: {orig_size} bytes')
    print(f'TFLite size: {tflite_size} bytes')
    print('Conversion complete.')
except Exception as e:
    print('Conversion failed:', e)
    sys.exit(2)
