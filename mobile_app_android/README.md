# Tomato Disease Android App (Kotlin + TFLite)

This folder contains a sample Android application that performs on-device inference using a TensorFlow Lite Inception V3 model (299x299 input).

Quick notes:
- Place your converted TFLite model at `app/src/main/assets/inception_v3_299.tflite`.
- `labels.txt` is under `app/src/main/assets/labels.txt` and contains class names.
- Open the project in Android Studio (use the `mobile_app_android` folder as the project root).

Build and run:
1. Open in Android Studio.
2. Sync Gradle and ensure SDK/NDK as required.
3. Run on a physical device (camera features require device).
