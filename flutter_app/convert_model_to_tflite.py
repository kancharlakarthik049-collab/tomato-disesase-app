#!/usr/bin/env python3
"""
TensorFlow Lite Model Converter for Tomato Disease Classification
==================================================================
This script converts a Keras/TensorFlow InceptionV3 model to TensorFlow Lite format
optimized for mobile deployment on Android devices.

Model Specifications:
- Input: 299x299x3 RGB images
- Output: Probability distribution over 10 tomato disease classes
- Preprocessing: Normalize to [-1, 1] range

Usage:
    python convert_model_to_tflite.py --model_path ../models/tomato_model.h5 --output_path assets/tomato_disease_model.tflite

Author: Tomato Disease Detector Team
Date: 2026
"""

import os
import sys
import argparse
import numpy as np

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")
except ImportError:
    print("ERROR: TensorFlow is not installed.")
    print("Please install it using: pip install tensorflow")
    sys.exit(1)


def validate_model_path(model_path: str) -> None:
    """Validate that the model file exists and has correct extension."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    valid_extensions = ['.h5', '.keras', '.pb', '']
    ext = os.path.splitext(model_path)[1].lower()
    
    if ext not in valid_extensions and not os.path.isdir(model_path):
        raise ValueError(f"Invalid model format. Expected .h5, .keras, or SavedModel directory")
    
    print(f"✓ Model file validated: {model_path}")


def load_keras_model(model_path: str) -> tf.keras.Model:
    """
    Load a Keras model from .h5 or .keras file.
    
    Args:
        model_path: Path to the saved Keras model
        
    Returns:
        Loaded Keras model
    """
    print(f"\n📥 Loading model from: {model_path}")
    
    try:
        # Try loading with custom objects for InceptionV3
        model = tf.keras.models.load_model(model_path, compile=False)
        print(f"✓ Model loaded successfully")
        print(f"  - Input shape: {model.input_shape}")
        print(f"  - Output shape: {model.output_shape}")
        print(f"  - Total parameters: {model.count_params():,}")
        return model
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}")
        raise


def load_saved_model(model_path: str) -> tf.keras.Model:
    """
    Load a TensorFlow SavedModel.
    
    Args:
        model_path: Path to SavedModel directory
        
    Returns:
        Loaded model
    """
    print(f"\n📥 Loading SavedModel from: {model_path}")
    
    try:
        model = tf.saved_model.load(model_path)
        print(f"✓ SavedModel loaded successfully")
        return model
    except Exception as e:
        print(f"ERROR: Failed to load SavedModel: {e}")
        raise


def convert_to_tflite(
    model: tf.keras.Model,
    output_path: str,
    optimize: bool = True,
    quantize: bool = False,
    representative_dataset: callable = None
) -> str:
    """
    Convert Keras model to TensorFlow Lite format.
    
    Args:
        model: Keras model to convert
        output_path: Path for output .tflite file
        optimize: Whether to apply default optimizations
        quantize: Whether to apply full integer quantization
        representative_dataset: Generator function for quantization calibration
        
    Returns:
        Path to the saved .tflite model
    """
    print(f"\n🔄 Converting model to TensorFlow Lite format...")
    
    # Create converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Apply optimizations
    if optimize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        print("  - Applied DEFAULT optimizations (recommended for mobile)")
    
    # Apply quantization if requested
    if quantize and representative_dataset:
        converter.representative_dataset = representative_dataset
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.uint8
        converter.inference_output_type = tf.uint8
        print("  - Applied full integer quantization")
    
    # Set experimental options for better compatibility
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,  # Standard TFLite ops
        tf.lite.OpsSet.SELECT_TF_OPS     # Selected TF ops (fallback)
    ]
    converter._experimental_lower_tensor_list_ops = False
    
    try:
        # Convert the model
        tflite_model = converter.convert()
        print(f"✓ Model converted successfully")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Save the model
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        # Get file size
        model_size = os.path.getsize(output_path)
        size_mb = model_size / (1024 * 1024)
        
        print(f"✓ Model saved to: {output_path}")
        print(f"  - File size: {size_mb:.2f} MB ({model_size:,} bytes)")
        
        return output_path
        
    except Exception as e:
        print(f"ERROR: Conversion failed: {e}")
        raise


def verify_tflite_model(tflite_path: str) -> None:
    """
    Verify that the TFLite model loads correctly and can perform inference.
    
    Args:
        tflite_path: Path to the .tflite model file
    """
    print(f"\n🔍 Verifying TFLite model...")
    
    try:
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=tflite_path)
        interpreter.allocate_tensors()
        
        # Get input details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print(f"✓ Model loaded successfully in TFLite interpreter")
        print(f"\n  Input Details:")
        for i, inp in enumerate(input_details):
            print(f"    [{i}] Name: {inp['name']}")
            print(f"        Shape: {inp['shape']}")
            print(f"        Type: {inp['dtype']}")
        
        print(f"\n  Output Details:")
        for i, out in enumerate(output_details):
            print(f"    [{i}] Name: {out['name']}")
            print(f"        Shape: {out['shape']}")
            print(f"        Type: {out['dtype']}")
        
        # Test inference with random data
        input_shape = input_details[0]['shape']
        input_dtype = input_details[0]['dtype']
        
        # Create test input (normalized like InceptionV3 expects)
        test_input = np.random.uniform(-1, 1, input_shape).astype(input_dtype)
        
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()
        
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        print(f"\n  Test Inference:")
        print(f"    Input shape: {test_input.shape}")
        print(f"    Output shape: {output_data.shape}")
        print(f"    Output sum (should be ~1.0 for softmax): {output_data.sum():.4f}")
        print(f"    Max confidence: {output_data.max():.4f}")
        
        print(f"\n✅ TFLite model verification PASSED")
        
    except Exception as e:
        print(f"❌ Model verification FAILED: {e}")
        raise


def create_representative_dataset():
    """
    Generator function for quantization calibration.
    Creates random samples matching InceptionV3 input format.
    
    For better quantization, use actual training images instead.
    """
    for _ in range(100):
        # Generate random image normalized to [-1, 1]
        data = np.random.uniform(-1, 1, (1, 299, 299, 3)).astype(np.float32)
        yield [data]


def main():
    """Main entry point for model conversion."""
    parser = argparse.ArgumentParser(
        description='Convert TensorFlow/Keras model to TFLite for Android deployment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic conversion:
    python convert_model_to_tflite.py --model_path ../models/tomato_model.h5
    
  With custom output path:
    python convert_model_to_tflite.py --model_path ../models/tomato_model.h5 --output_path assets/model.tflite
    
  With quantization for smaller size:
    python convert_model_to_tflite.py --model_path ../models/tomato_model.h5 --quantize
        """
    )
    
    parser.add_argument(
        '--model_path',
        type=str,
        default='../models/tomato_model.h5',
        help='Path to the Keras model (.h5, .keras) or SavedModel directory'
    )
    
    parser.add_argument(
        '--output_path',
        type=str,
        default='assets/tomato_disease_model.tflite',
        help='Output path for the TFLite model'
    )
    
    parser.add_argument(
        '--no-optimize',
        action='store_true',
        help='Disable optimization (not recommended)'
    )
    
    parser.add_argument(
        '--quantize',
        action='store_true',
        help='Apply full integer quantization (smaller size, may reduce accuracy)'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        default=True,
        help='Verify the converted model (default: True)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Tomato Disease Model Converter - TensorFlow to TFLite")
    print("=" * 60)
    
    try:
        # Validate input
        validate_model_path(args.model_path)
        
        # Load model
        if os.path.isdir(args.model_path):
            model = load_saved_model(args.model_path)
        else:
            model = load_keras_model(args.model_path)
        
        # Convert to TFLite
        rep_dataset = create_representative_dataset if args.quantize else None
        output_path = convert_to_tflite(
            model=model,
            output_path=args.output_path,
            optimize=not args.no_optimize,
            quantize=args.quantize,
            representative_dataset=rep_dataset
        )
        
        # Verify the converted model
        if args.verify:
            verify_tflite_model(output_path)
        
        print("\n" + "=" * 60)
        print("  ✅ CONVERSION COMPLETE")
        print("=" * 60)
        print(f"\nNext steps:")
        print(f"  1. Copy {output_path} to your Flutter app's assets folder")
        print(f"  2. Update pubspec.yaml to include the asset")
        print(f"  3. Build your app with: flutter build apk --release")
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check that your model file exists at the specified path.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
