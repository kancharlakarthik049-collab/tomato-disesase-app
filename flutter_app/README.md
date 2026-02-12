# Tomato Disease Detector - Flutter Android Application

A complete Flutter Android application for identifying tomato plant diseases using deep learning (InceptionV3 model) with TensorFlow Lite.

## Features

- **Camera Capture**: Take photos of tomato leaves directly
- **Gallery Selection**: Choose images from device gallery
- **Real-time Prediction**: On-device AI inference
- **Offline Support**: Works without internet connection
- **Professional UI**: Material Design 3 interface
- **Detailed Results**: Confidence scores and top predictions

## Disease Classes

The model can identify 10 tomato conditions:

1. Bacterial Spot
2. Early Blight
3. Late Blight
4. Leaf Mold
5. Septoria Leaf Spot
6. Spider Mites
7. Target Spot
8. Yellow Leaf Curl Virus
9. Tomato Mosaic Virus
10. Healthy

---

## Prerequisites

### Required Software

1. **Flutter SDK** (3.0.0 or later)
   - Download: https://flutter.dev/docs/get-started/install
   - Add to PATH

2. **Android Studio** (for Android SDK)
   - Download: https://developer.android.com/studio
   - Install Android SDK 34 (compileSdk)
   - Install Android SDK 21+ (minSdk)

3. **Python 3.8+** (for model conversion)
   - Required packages: `tensorflow`

### Verify Installation

```powershell
# Check Flutter
flutter doctor

# Check Python
python --version
```

---

## Quick Start

### Step 1: Convert Model to TensorFlow Lite

```powershell
# Navigate to flutter app directory
cd flutter_app

# Install TensorFlow
pip install tensorflow

# Convert model
python convert_model_to_tflite.py --model_path ../models/tomato_model.h5

# Move model to assets
move assets\tomato_disease_model.tflite tomato_disease_detector\assets\
```

### Step 2: Build the APK

**Option A: Using Build Script (Recommended)**
```powershell
# Windows PowerShell
.\build_apk.ps1

# Or using batch file
.\build_apk.bat
```

**Option B: Manual Build**
```powershell
cd tomato_disease_detector

# Get dependencies
flutter pub get

# Build release APK
flutter build apk --release
```

### Step 3: Install APK

```powershell
# Using ADB
adb install build/app/outputs/flutter-apk/app-release.apk

# Or copy APK to phone and install manually
```

---

## Project Structure

```
flutter_app/
├── convert_model_to_tflite.py    # Model conversion script
├── build_apk.ps1                  # PowerShell build script
├── build_apk.bat                  # Batch build script
└── tomato_disease_detector/       # Flutter project
    ├── pubspec.yaml              # Dependencies
    ├── assets/
    │   ├── tomato_disease_model.tflite  # TFLite model
    │   └── labels.txt            # Disease labels
    ├── lib/
    │   ├── main.dart             # App entry point
    │   ├── screens/
    │   │   └── home_screen.dart  # Main screen
    │   ├── services/
    │   │   └── classifier_service.dart  # TFLite inference
    │   ├── models/
    │   │   └── prediction_result.dart   # Result model
    │   └── widgets/
    │       ├── image_preview_widget.dart
    │       ├── prediction_result_widget.dart
    │       └── action_buttons_widget.dart
    └── android/
        ├── app/
        │   ├── build.gradle      # App build config
        │   ├── proguard-rules.pro
        │   └── src/main/
        │       ├── AndroidManifest.xml
        │       └── kotlin/...
        └── build.gradle          # Project build config
```

---

## Detailed Setup Guide

### Model Conversion

The InceptionV3 model must be converted to TensorFlow Lite format:

```python
# Full conversion command with options
python convert_model_to_tflite.py \
    --model_path ../models/tomato_model.h5 \
    --output_path tomato_disease_detector/assets/tomato_disease_model.tflite \
    --verify
```

**Conversion Options:**
- `--model_path`: Path to Keras model (.h5 or SavedModel)
- `--output_path`: Output path for .tflite file
- `--quantize`: Apply quantization (smaller size, may reduce accuracy)
- `--no-optimize`: Disable optimizations
- `--verify`: Verify converted model

### Building for Release

```powershell
cd tomato_disease_detector

# Clean build
flutter clean

# Get fresh dependencies
flutter pub get

# Build optimized release APK
flutter build apk --release --obfuscate --split-debug-info=build/debug-info

# Or build App Bundle for Play Store
flutter build appbundle --release
```

**Build Outputs:**
- APK: `build/app/outputs/flutter-apk/app-release.apk`
- AAB: `build/app/outputs/bundle/release/app-release.aab`

---

## Testing

### Testing Checklist

- [ ] Camera capture works
- [ ] Gallery selection works
- [ ] Images load correctly
- [ ] Model predicts correctly
- [ ] Results display properly
- [ ] Loading indicators show
- [ ] Error handling works
- [ ] Orientation changes handled
- [ ] Works offline
- [ ] Performance is acceptable (<3s inference)

### Test on Device

```powershell
# Run in debug mode on connected device
flutter run

# Run with verbose logging
flutter run -v

# Run on specific device
flutter devices
flutter run -d <device_id>
```

### Test APK

```powershell
# Install on device
adb install -r build/app/outputs/flutter-apk/app-release.apk

# Uninstall
adb uninstall com.example.tomato_disease_detector
```

---

## Troubleshooting

### Common Issues

#### 1. Model Loading Error

**Symptom:** "Failed to load model" error

**Solutions:**
- Verify model file exists: `assets/tomato_disease_model.tflite`
- Check pubspec.yaml includes assets section
- Run `flutter pub get` again
- Clean and rebuild: `flutter clean && flutter pub get && flutter build apk`

#### 2. Camera Permission Denied

**Symptom:** Camera doesn't open

**Solutions:**
- Check AndroidManifest.xml has camera permission
- Enable camera permission in device settings
- Uninstall and reinstall app

#### 3. Build Errors

**Symptom:** Gradle build fails

**Solutions:**
```powershell
# Update Gradle
cd android
./gradlew wrapper --gradle-version=8.3

# Clean Gradle cache
./gradlew clean

# Rebuild
cd ..
flutter build apk
```

#### 4. TFLite Compatibility

**Symptom:** Model inference crashes

**Solutions:**
- Ensure model was converted with TF 2.x
- Check model input/output shapes match code
- Try without optimizations: `--no-optimize`

#### 5. Image Processing Errors

**Symptom:** "Failed to decode image" error

**Solutions:**
- Ensure image format is supported (jpg, png)
- Reduce image quality in image_picker
- Check device storage permissions

### Performance Optimization

1. **Model Size**: Use quantization to reduce model size
2. **Image Size**: Reduce image quality before processing
3. **Threads**: Classifier uses 4 threads by default
4. **Memory**: Close unused activities

---

## Distribution

### Sharing APK File

1. Build release APK: `flutter build apk --release`
2. Locate: `build/app/outputs/flutter-apk/app-release.apk`
3. Rename if desired: `TomatoDiseaseDetector_v1.0.apk`
4. Share via email, cloud storage, or direct transfer

### Google Play Store

1. Build App Bundle: `flutter build appbundle --release`
2. Create Google Play Developer account ($25 one-time fee)
3. Prepare store listing:
   - App icon (512x512 PNG)
   - Feature graphic (1024x500 PNG)
   - Screenshots
   - Description
   - Privacy policy URL
4. Upload AAB file
5. Complete content rating questionnaire
6. Set pricing (free/paid)
7. Submit for review

### Privacy Policy

For apps using camera/gallery, include privacy policy stating:
- What data is collected (images for analysis only)
- How data is used (local processing only, no upload)
- Data storage (no persistent storage)
- User consent (camera/gallery permission prompts)

---

## Customization

### Changing App Name

Edit: `android/app/src/main/AndroidManifest.xml`
```xml
android:label="Your App Name"
```

### Changing Package Name

1. Update: `android/app/build.gradle`
```gradle
applicationId "com.yourcompany.appname"
namespace "com.yourcompany.appname"
```

2. Rename folder: `android/app/src/main/kotlin/com/yourcompany/appname/`

3. Update: `MainActivity.kt`
```kotlin
package com.yourcompany.appname
```

### Adding App Icon

1. Generate icons: https://flutter.dev/docs/deployment/android#adding-a-launcher-icon
2. Or use: https://romannurik.github.io/AndroidAssetStudio/
3. Place in `android/app/src/main/res/mipmap-*/`

### Modifying Disease Labels

Edit: `assets/labels.txt`
- One label per line
- Order must match model output indices
- Labels are formatted automatically in code

---

## Technical Specifications

### Model Requirements

| Parameter | Value |
|-----------|-------|
| Input Size | 224 x 224 x 3 |
| Input Type | Float32 |
| Normalization | [0, 1] |
| Output | 10 class probabilities |

### Android Requirements

| Parameter | Value |
|-----------|-------|
| Minimum SDK | 21 (Android 5.0) |
| Target SDK | 34 (Android 14) |
| Compile SDK | 34 |

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| tflite_flutter | ^0.10.4 | TFLite inference |
| image_picker | ^1.0.7 | Camera/gallery |
| image | ^4.1.7 | Image processing |
| path_provider | ^2.1.2 | File paths |
| permission_handler | ^11.3.0 | Permissions |

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Verify all prerequisites are installed
3. Try clean rebuild
4. Check Flutter doctor output

---

## License

This project is provided as-is for educational purposes.
