"""
Python validation script to verify preprocessing matches Flutter
Run this in your Python environment where you trained the model

Usage:
    python scripts/validate_preprocessing.py

Note: This script is now ONNX-focused. If you use ONNX models, adjust logic accordingly.
"""

import numpy as np
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def validate_preprocessing(model_path: str = None, output_path: str = 'validation_results.json'):
    """
    Validate preprocessing and export results for Flutter comparison
    
    Args:
        model_path: Path to your ONNX model file (optional)
        output_path: Where to save validation results
    """
    
    print("=" * 60)
    print("🧪 PREPROCESSING VALIDATION SCRIPT")
    print("=" * 60)
    
    # Default input size (from app.py)
    input_size = 224
    
    # ONNX model loading not implemented here. If needed, add ONNX shape extraction logic.
    # Default input size (224) is used unless you add ONNX parsing.
    else:
        print(f"\n📋 Using default input size from app.py: {input_size}x{input_size}")
    
    # Create test images
    print("\n🎨 Creating test images...")
    test_images = {
        'black': np.zeros((1, input_size, input_size, 3), dtype=np.float32),
        'white': np.ones((1, input_size, input_size, 3), dtype=np.float32) * 255,
        'gray_127': np.ones((1, input_size, input_size, 3), dtype=np.float32) * 127,
        'gray_128': np.ones((1, input_size, input_size, 3), dtype=np.float32) * 128,
        'red': np.zeros((1, input_size, input_size, 3), dtype=np.float32),
        'green': np.zeros((1, input_size, input_size, 3), dtype=np.float32),
        'blue': np.zeros((1, input_size, input_size, 3), dtype=np.float32),
    }
    test_images['red'][:, :, :, 0] = 255
    test_images['green'][:, :, :, 1] = 255
    test_images['blue'][:, :, :, 2] = 255
    
    results = {
        'model_info': {
            'input_size': input_size,
        },
        'preprocessing_modes': {},
        'your_app_preprocessing': {}
    }
    
    # ====================
    # Test InceptionV3 preprocessing: (pixel / 127.5) - 1.0 → [-1, 1]
    # ====================
    print("\n" + "=" * 60)
    print("🔄 MODE 1: InceptionV3 Preprocessing")
    print("   Formula: (pixel / 127.5) - 1.0")
    print("   Range: [-1.0, 1.0]")
    print("=" * 60)
    
    inception_results = {}
    for name, img in test_images.items():
        preprocessed = (img / 127.5) - 1.0
        pixel_value = preprocessed[0, 0, 0].tolist()
        inception_results[name] = {
            'original': [int(img[0, 0, 0, i]) for i in range(3)],
            'preprocessed': [round(pixel_value[i], 4) for i in range(3)],
        }
        print(f"   {name:12s}: {inception_results[name]['original']} → {inception_results[name]['preprocessed']}")
    
    results['preprocessing_modes']['inception_v3'] = {
        'formula': '(pixel / 127.5) - 1.0',
        'range': '[-1.0, 1.0]',
        'test_values': inception_results,
    }
    
    # ====================
    # Test Rescale preprocessing: pixel / 255.0 → [0, 1]
    # ====================
    print("\n" + "=" * 60)
    print("🔄 MODE 2: Rescale Preprocessing")
    print("   Formula: pixel / 255.0")
    print("   Range: [0.0, 1.0]")
    print("=" * 60)
    
    rescale_results = {}
    for name, img in test_images.items():
        preprocessed = img / 255.0
        pixel_value = preprocessed[0, 0, 0].tolist()
        rescale_results[name] = {
            'original': [int(img[0, 0, 0, i]) for i in range(3)],
            'preprocessed': [round(pixel_value[i], 4) for i in range(3)],
        }
        print(f"   {name:12s}: {rescale_results[name]['original']} → {rescale_results[name]['preprocessed']}")
    
    results['preprocessing_modes']['rescale'] = {
        'formula': 'pixel / 255.0',
        'range': '[0.0, 1.0]',
        'test_values': rescale_results,
    }
    
    # ====================
    # Check YOUR app.py preprocessing
    # ====================
    print("\n" + "=" * 60)
    print("📋 YOUR APP.PY PREPROCESSING")
    print("=" * 60)
    
    # Read app.py to confirm preprocessing
    app_py_path = Path(__file__).parent.parent / 'app.py'
    if app_py_path.exists():
        with open(app_py_path, 'r') as f:
            content = f.read()
        
        if '/ 255.0' in content or '/255.0' in content or '/ 255' in content:
            print("   ✅ Found: / 255.0 (Rescale mode)")
            results['your_app_preprocessing']['mode'] = 'rescale'
            results['your_app_preprocessing']['formula'] = 'pixel / 255.0'
            results['your_app_preprocessing']['range'] = '[0.0, 1.0]'
        elif '/ 127.5' in content:
            print("   ✅ Found: / 127.5 (InceptionV3 mode)")
            results['your_app_preprocessing']['mode'] = 'inception_v3'
            results['your_app_preprocessing']['formula'] = '(pixel / 127.5) - 1.0'
            results['your_app_preprocessing']['range'] = '[-1.0, 1.0]'
        
        if 'resize((224, 224))' in content or 'resize((224,224))' in content:
            print("   ✅ Found: resize((224, 224))")
            results['your_app_preprocessing']['input_size'] = 224
        elif 'resize((299, 299))' in content or 'resize((299,299))' in content:
            print("   ✅ Found: resize((299, 299))")
            results['your_app_preprocessing']['input_size'] = 299
    else:
        print("   ⚠️ app.py not found")
    
    # ====================
    # Determine recommendation
    # ====================
    if results['your_app_preprocessing'].get('mode') == 'rescale':
        results['recommended_mode'] = 'rescale'
        results['recommended_settings'] = {
            'input_size': results['your_app_preprocessing'].get('input_size', 224),
            'normalization': 'pixel / 255.0',
            'range': '[0.0, 1.0]'
        }
    else:
        results['recommended_mode'] = 'inception_v3'
        results['recommended_settings'] = {
            'input_size': 299,
            'normalization': '(pixel / 127.5) - 1.0',
            'range': '[-1.0, 1.0]'
        }
    
    # ====================
    # Print comparison table
    # ====================
    print("\n" + "=" * 60)
    print("📊 COMPARISON TABLE")
    print("=" * 60)
    print("┌─────────────┬────────────────────────┬────────────────────────┐")
    print("│ Test Image  │ InceptionV3            │ Rescale                │")
    print("├─────────────┼────────────────────────┼────────────────────────┤")
    
    for name in ['black', 'white', 'gray_127', 'gray_128']:
        inc_val = inception_results[name]['preprocessed']
        res_val = rescale_results[name]['preprocessed']
        print(f"│ {name:11s} │ ({inc_val[0]:6.3f},{inc_val[1]:6.3f},{inc_val[2]:6.3f}) │ ({res_val[0]:6.3f},{res_val[1]:6.3f},{res_val[2]:6.3f}) │")
    
    print("└─────────────┴────────────────────────┴────────────────────────┘")
    
    # ====================
    # Print recommendation
    # ====================
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION")
    print("=" * 60)
    print(f"   Based on your app.py:")
    print(f"   ✅ Mode: {results['recommended_mode'].upper()}")
    print(f"   ✅ Input size: {results['recommended_settings']['input_size']}x{results['recommended_settings']['input_size']}")
    print(f"   ✅ Normalization: {results['recommended_settings']['normalization']}")
    print(f"   ✅ Range: {results['recommended_settings']['range']}")
    
    # ====================
    # Flutter code to match
    # ====================
    print("\n" + "=" * 60)
    print("📱 FLUTTER CODE SHOULD USE:")
    print("=" * 60)
    
    if results['recommended_mode'] == 'rescale':
        print("""
    // classifier_service.dart
    static const int inputSize = 224;
    
    // Preprocessing - match Python: / 255.0
    final r = pixel.r.toDouble() / 255.0;
    final g = pixel.g.toDouble() / 255.0;
    final b = pixel.b.toDouble() / 255.0;
    """)
    else:
        print("""
    // classifier_service.dart
    static const int inputSize = 299;
    
    // Preprocessing - InceptionV3: (pixel / 127.5) - 1.0
    final r = (pixel.r.toDouble() / 127.5) - 1.0;
    final g = (pixel.g.toDouble() / 127.5) - 1.0;
    final b = (pixel.b.toDouble() / 127.5) - 1.0;
    """)
    
    # Save results
    output_file = Path(__file__).parent.parent / output_path
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    
    print("\n" + "=" * 60)
    print("🔄 NEXT STEPS")
    print("=" * 60)
    print("1. Verify Flutter app uses the recommended settings")
    print("2. Run the app and tap 🐛 debug button")
    print("3. Compare preprocessing values")
    print("4. If values match, predictions should be correct!")
    print("=" * 60 + "\n")
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate preprocessing for TFLite model')
    parser.add_argument('--model', type=str, default=None, 
                        help='Path to model file (.h5 or .tflite)')
    parser.add_argument('--output', type=str, default='validation_results.json',
                        help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Default model paths to try
    model_paths = [
        args.model,
        'models/tomato_model.h5',
        'models/tomato_model.tflite',
    ]
    
    model_path = None
    for path in model_paths:
        if path and Path(path).exists():
            model_path = path
            break
    
    validate_preprocessing(model_path, args.output)
