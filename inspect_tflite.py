import os
import sys

def inspect(path):
    try:
        import tensorflow as tf
    except Exception as e:
        print('TensorFlow not available:', e)
        return

    if not os.path.exists(path):
        print(f'Not found: {path}')
        return

    try:
        print('\nInspecting:', path)
        interpreter = tf.lite.Interpreter(model_path=path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        print('Inputs:')
        for d in input_details:
            print('  shape:', d['shape'], 'dtype:', d['dtype'], 'name:', d.get('name'))
        print('Outputs:')
        for d in output_details:
            print('  shape:', d['shape'], 'dtype:', d['dtype'], 'name:', d.get('name'))
    except Exception as e:
        print('Failed to inspect', path, 'error:', e)

if __name__ == '__main__':
    candidates = [
        'models/tomato_model.tflite',
        'models/tomato_model.h5',
    ]
    for c in candidates:
        inspect(c)
