"""
Quantize tomato_model.h5 to a TFLite model.

Usage:
  python quantize_model.py --input models/tomato_model.h5 --out models/tomato_model.tflite

This script performs float16 post-training quantization (good balance of size/compatibility).
If TensorFlow is not available or conversion fails, it will report an error.
"""
import argparse
import os
import sys


def quantize_to_float16(input_path, out_path):
    try:
        import tensorflow as tf
    except Exception as e:
        print('TensorFlow is required for quantization:', e)
        return False

    if not os.path.exists(input_path):
        print('Input model not found:', input_path)
        return False

    print('Loading Keras model from', input_path)
    try:
        model = tf.keras.models.load_model(input_path)
    except Exception as e:
        print('Failed to load Keras model:', e)
        return False

    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        # Use float16 quantization for broad device support
        converter.target_spec.supported_types = [tf.float16]
        tflite_model = converter.convert()

        out_dir = os.path.dirname(out_path)
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(tflite_model)
        print('Wrote quantized TFLite model to', out_path)
        return True
    except Exception as e:
        print('Quantization failed:', e)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='models/tomato_model.h5')
    parser.add_argument('--out', '-o', default='models/tomato_model.tflite')
    args = parser.parse_args()

    ok = quantize_to_float16(args.input, args.out)
    if not ok:
        sys.exit(2)


if __name__ == '__main__':
    main()
