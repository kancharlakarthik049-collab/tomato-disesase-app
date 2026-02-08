# Tomato Disease Mobile (Expo)

This is a minimal Expo React Native app that uploads an image to the Flask backend and displays the prediction.

Quick start:

1. Install dependencies (requires Node.js and Expo CLI):

```bash
cd mobile_app
npm install
# or: yarn
```

2. Update `BACKEND_URL` in `App.js` to point to your running Flask server (include port), e.g. `http://192.168.1.10:5000`.

3. Start Expo:

```bash
npm start
# then open on device via QR or emulator
```

Notes:
- For Android emulator, `localhost` is not the same as host. Use your machine LAN IP or `10.0.2.2` for some emulators.
- The Flask backend must have `app.run(host='0.0.0.0')` when running on a different machine or container.
