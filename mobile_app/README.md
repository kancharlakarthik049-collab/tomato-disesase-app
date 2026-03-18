# Tomato Disease Identification - Mobile App

This is an Expo-based React Native mobile application for iOS and Android that uses AI to identify tomato leaf diseases.

## Features

- 📸 **Camera & Gallery**: Capture or select tomato leaf images
- 🤖 **AI Diagnosis**: Real-time disease classification with confidence scores
- 🎨 **Green Detection**: Visual mask showing detected leaf regions
- 📊 **Detailed Results**: Full probability distribution across all disease classes
- 💊 **Recommendations**: Treatment suggestions for each detected disease

## Supported Diseases

1. Bacterial Spot
2. Early Blight
3. Late Blight
4. Leaf Mold
5. Septoria Leaf Spot
6. Spider Mites
7. Target Spot
8. Yellow Leaf Curl Virus
9. Mosaic Virus
10. Healthy (no disease)

## Quick Start

### Prerequisites

- Node.js (v16+)
- Expo CLI: `npm install -g expo-cli`
- Expo Go app on your Android/iOS device (free from app store)

### Installation

```bash
cd mobile_app
npm install
```

### Development

Run the development server:

```bash
npx expo start
```

Then:
- **Android**: Press `a` or scan the QR code with Expo Go app
- **iOS**: Press `i` or scan the QR code with Camera app → Open with Expo Go
- **Web**: Press `w`

## Building for Deployment

### Android APK (Standalone)

```bash
npm install -g eas-cli
eas login  # Sign up at eas.expo.dev
eas build:configure
eas build -p android --profile preview
```

This generates a downloadable `.apk` file that works on any Android device.

### iOS Build (Requires Apple Developer Account)

```bash
eas build -p ios --profile preview
```

## Configuration

Update the backend URL in `App.js`:

```javascript
const BACKEND_URL = 'https://your-render-domain.onrender.com';
```

## API Endpoint

The app connects to `/api/predict` on your backend:

**Request:**
- Method: POST
- Body: multipart/form-data with `file` field

**Response:**
```json
{
  "filename": "leaf.jpg",
  "prediction": "Early_blight",
  "confidence": 0.94,
  "mask": "<base64 PNG>",
  "all_predictions": {
    "Bacterial_spot": 0.02,
    "Early_blight": 0.94,
    ...
  }
}
```

## Permissions

- **Android**: Camera, Photo Library
- **iOS**: Camera, Photo Library

Users are prompted to grant permissions when needed.

## Troubleshooting

### App won't connect to backend
- Ensure backend is running and accessible at `BACKEND_URL`
- Check network connectivity
- Use ngrok for local testing: `ngrok http 5000`

### Image upload fails
- Check file size (max 16MB)
- Ensure image format is PNG, JPG, or JPEG
- Verify camera/gallery permissions are granted

### Model not found error
- Ensure ONNX model is deployed on backend
- Check `GOOGLE_DRIVE_MODEL_ID` environment variable is set

## Architecture

```
mobile_app/
├── App.js              # Main component with UI and API calls
├── app.json            # Expo configuration
├── package.json        # Dependencies
└── assets/             # Icons, splash screens (optional)
```

## Dependencies

- `expo`: ~51.0.0
- `expo-image-picker`: Image selection and camera
- `react-native`: UI framework
- `react`: ~18.2.0

## License

MIT - See LICENSE file in project root
