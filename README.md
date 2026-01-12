# 🍅 Tomato Disease Classification Web App

A Flask-based web application that uses deep learning to classify tomato leaf diseases from uploaded images.

## Features

- Upload and classify tomato leaf images
- Predicts 10 different tomato plant conditions
- Real-time image processing and classification
- Clean, responsive web interface
- Displays prediction confidence scores

## Project Structure

```
tomato_disease_app/
│
├── app.py                   # Flask backend code
├── requirements.txt         # List of dependencies
├── models/                  # Folder to store trained model
│   └── README.md           # Model placement instructions
├── dataset/                # Empty dataset folder
│   ├── train/              
│   └── val/
├── templates/
│   └── index.html          # HTML template
├── static/
│   ├── style.css          # CSS styling
│   └── uploads/           # Uploaded images stored here
```

## Setup Instructions

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place your trained model:
   - Put your trained Keras model file `tomato_model.h5` in the `models/` directory
   - The model should be configured for input shape (224, 224, 3)
   - Should predict 10 classes: Bacterial spot, Early blight, Late blight, etc.

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the web interface:
   - Open your browser and navigate to `http://localhost:5000`
   - The health check endpoint is available at `http://localhost:5000/health`

## Usage

1. Open the web interface in your browser
2. Click "Choose File" to select a tomato leaf image
3. Click "Analyze Image" to get the prediction
4. View the results showing:
   - Uploaded image
   - Predicted condition
   - Confidence score

<<<<<<< HEAD
Mobile app (Expo)
------------------

An Expo React Native app is included in `mobile_app/`.

Quick start:

```bash
cd mobile_app
npm install
npm start
```

Edit `mobile_app/App.js` and set `BACKEND_URL` to point to your running Flask server, e.g. `http://192.168.1.10:5000`.

On-device inference (optional)
-----------------------------

You can convert the provided Keras model to TensorFlow Lite for on-device inference using:

```bash
python convert_to_tflite.py
```

This writes `models/tomato_model.tflite` which can be integrated into native Android/iOS or used with TensorFlow Lite interpreters.

Running tests
-------------

Run the simple health check test (make sure the server is running):

```bash
pip install pytest
pytest tests/test_api_health.py
```

=======
>>>>>>> a17aef9ddcd5f1388b27f3a97ec1ef9a16beaa98
## Supported Image Formats

- JPG/JPEG
- PNG

## Model Information

The application expects a Keras model trained to classify the following conditions:
- Bacterial_spot
- Early_blight
- Late_blight
- Leaf_Mold
- Septoria_leaf_spot
- Spider_mites
- Target_Spot
- Yellow_Leaf_Curl_Virus
- Mosaic_virus
- Healthy

## Error Handling

- Provides friendly error messages for:
  - Missing model file
  - Invalid file types
  - File processing errors
  - Invalid image formats

## Contributing

Feel free to contribute to this project by:
1. Opening issues
2. Suggesting enhancements
3. Creating pull requests

## License

This project is open source and available under the MIT License.

## Deployment

Below are two simple ways to deploy the application: Heroku (quick) and Docker (portable).

Heroku
- Ensure you have the Heroku CLI installed and are logged in.
- Create a new app and push:

```bash
heroku create your-app-name
git push heroku main
heroku ps:scale web=1
heroku logs --tail
```

Notes:
- The included `Procfile` runs `gunicorn app:app`. Ensure `tomato_model.h5` is present in the `models/` directory — consider storing the model in cloud storage and downloading at runtime if it is large.

Docker
- Build the image and run locally:

```bash
docker build -t tomato-disease-app .
docker run -p 5000:5000 --env PORT=5000 tomato-disease-app
```

- Push to a container registry (Docker Hub, GitHub Container Registry) then deploy to your cloud provider (AWS ECS, Azure Container Instances, Google Cloud Run, etc.).

Example push to Docker Hub:

```bash
docker tag tomato-disease-app yourdockerhubusername/tomato-disease-app:latest
docker push yourdockerhubusername/tomato-disease-app:latest

Leaf-detector (optional)

- You can improve upload filtering by training an optional binary `leaf` / `nonleaf` detector. See `leaf_detector/train_detector.py`.
- Prepare training data in `leaf_detector_data/train` and `leaf_detector_data/val` with `leaf/` and `nonleaf/` subfolders.
- Run `python leaf_detector/train_detector.py` to create `models/leaf_detector.h5`.
- When `models/leaf_detector.h5` is present the app will use it (lazy-load) to reject non-leaf images before classification.

Configuration via environment variables

- `GREEN_H_MIN`, `GREEN_H_MAX`, `S_MIN`, `V_MIN`, `GREEN_PROP_THRESH` — tune the HSV heuristic used if you don't use the detector. Defaults are safe starting points.

CI / Container registry

- A GitHub Actions workflow is included at `.github/workflows/docker-build.yml` to build and push the image to GitHub Container Registry (adjust tags/secrets to your registry).
```

Local testing
- Run locally in development mode:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
python app.py
```
