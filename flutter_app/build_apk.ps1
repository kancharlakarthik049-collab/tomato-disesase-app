# ============================================================
# Tomato Disease Detector - Build Script (PowerShell)
# ============================================================
# This script automates the complete build process

param(
    [switch]$Debug,
    [switch]$AppBundle,
    [switch]$Clean,
    [switch]$SkipModelCheck
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Tomato Disease Detector - Build Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Define paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Join-Path $ScriptDir "tomato_disease_detector"
$ModelPath = Join-Path $ProjectDir "assets\tomato_disease_model.tflite"
$LabelsPath = Join-Path $ProjectDir "assets\labels.txt"

# Navigate to project directory
Set-Location $ProjectDir

# Check Flutter installation
Write-Host "[1/6] Checking Flutter installation..." -ForegroundColor Yellow
try {
    $flutterVersion = & flutter --version 2>&1
    Write-Host $flutterVersion
} catch {
    Write-Host "ERROR: Flutter is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Flutter from https://flutter.dev"
    exit 1
}

# Clean if requested
if ($Clean) {
    Write-Host ""
    Write-Host "[2/6] Cleaning previous build..." -ForegroundColor Yellow
    & flutter clean
} else {
    Write-Host "[2/6] Skipping clean (use -Clean to clean first)" -ForegroundColor Gray
}

# Get dependencies
Write-Host ""
Write-Host "[3/6] Getting dependencies..." -ForegroundColor Yellow
& flutter pub get
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to get dependencies" -ForegroundColor Red
    exit 1
}

# Check model file
Write-Host ""
Write-Host "[4/6] Checking assets..." -ForegroundColor Yellow

if (-not $SkipModelCheck) {
    if (-not (Test-Path $ModelPath)) {
        Write-Host "WARNING: Model file not found!" -ForegroundColor Yellow
        Write-Host "  Expected: $ModelPath" -ForegroundColor Gray
        Write-Host ""
        Write-Host "To convert your model, run:" -ForegroundColor Cyan
        Write-Host "  python convert_model_to_tflite.py --model_path ../models/tomato_model.h5"
        Write-Host ""
        
        $response = Read-Host "Continue without model? (y/N)"
        if ($response.ToLower() -ne "y") {
            exit 1
        }
    } else {
        $modelSize = (Get-Item $ModelPath).Length / 1MB
        Write-Host "  Model found: $($modelSize.ToString('F2')) MB" -ForegroundColor Green
    }
    
    if (Test-Path $LabelsPath) {
        $labelCount = (Get-Content $LabelsPath | Where-Object { $_.Trim() -ne "" }).Count
        Write-Host "  Labels found: $labelCount classes" -ForegroundColor Green
    }
}

# Run Flutter doctor
Write-Host ""
Write-Host "[5/6] Running Flutter doctor..." -ForegroundColor Yellow
& flutter doctor

# Build
Write-Host ""
Write-Host "[6/6] Building application..." -ForegroundColor Yellow

if ($AppBundle) {
    Write-Host "Building App Bundle (AAB)..." -ForegroundColor Cyan
    if ($Debug) {
        & flutter build appbundle --debug
    } else {
        & flutter build appbundle --release
    }
    $OutputPath = "build\app\outputs\bundle\release\app-release.aab"
} else {
    Write-Host "Building APK..." -ForegroundColor Cyan
    if ($Debug) {
        & flutter build apk --debug
        $OutputPath = "build\app\outputs\flutter-apk\app-debug.apk"
    } else {
        & flutter build apk --release
        $OutputPath = "build\app\outputs\flutter-apk\app-release.apk"
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

# Success
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output: $OutputPath" -ForegroundColor Cyan

$fullPath = Join-Path $ProjectDir $OutputPath
if (Test-Path $fullPath) {
    $fileSize = (Get-Item $fullPath).Length / 1MB
    Write-Host "Size: $($fileSize.ToString('F2')) MB" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "To install on connected device:" -ForegroundColor Yellow
Write-Host "  adb install -r `"$OutputPath`""
Write-Host ""
Write-Host "To share: Copy the file from the path above" -ForegroundColor Yellow
Write-Host ""

# Open output folder
if (-not $AppBundle) {
    explorer (Split-Path $fullPath)
}
