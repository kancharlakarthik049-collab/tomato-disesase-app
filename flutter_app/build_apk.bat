@echo off
REM ============================================================
REM Tomato Disease Detector - Build Script (Windows)
REM ============================================================
REM This script builds the Flutter Android APK

echo.
echo ============================================================
echo    Tomato Disease Detector - Build Script
echo ============================================================
echo.

REM Navigate to project directory
cd /d "%~dp0tomato_disease_detector"

REM Check if Flutter is installed
where flutter >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Flutter is not installed or not in PATH
    echo Please install Flutter from https://flutter.dev
    pause
    exit /b 1
)

echo [1/5] Checking Flutter version...
flutter --version

echo.
echo [2/5] Getting dependencies...
call flutter pub get
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to get dependencies
    pause
    exit /b 1
)

echo.
echo [3/5] Checking for model file...
if not exist "assets\tomato_disease_model.tflite" (
    echo WARNING: Model file not found at assets\tomato_disease_model.tflite
    echo.
    echo Please run the model conversion script first:
    echo   python convert_model_to_tflite.py --model_path ../models/tomato_model.h5
    echo.
    echo Or copy your .tflite model to: assets\tomato_disease_model.tflite
    echo.
    set /p CONT="Continue without model? (y/n): "
    if /i not "%CONT%"=="y" exit /b 1
)

echo.
echo [4/5] Building release APK...
call flutter build apk --release
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [5/5] Build complete!
echo.
echo ============================================================
echo APK Location: build\app\outputs\flutter-apk\app-release.apk
echo ============================================================
echo.
echo You can install this APK on any Android device.
echo.

REM Open the output folder
explorer build\app\outputs\flutter-apk\

pause
