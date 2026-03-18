import os
import io
import logging
import json
import shutil
import base64
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import onnxruntime as ort
import cv2

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration constants
MODEL_PATH = os.getenv('MODEL_PATH', 'models/tomato_model.onnx')
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
CONF_THRESH = float(os.getenv('CONF_THRESH', 0.6))

# HSV threshold configuration (from env or defaults)
GREEN_H_MIN = int(os.getenv('GREEN_H_MIN', 25))
GREEN_H_MAX = int(os.getenv('GREEN_H_MAX', 100))
S_MIN = int(os.getenv('S_MIN', 40))
V_MIN = int(os.getenv('V_MIN', 40))
GREEN_PROP_THRESH = float(os.getenv('GREEN_PROP_THRESH', 0.03))

# App configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Debug folder
DEBUG_DIR = os.path.join(UPLOAD_FOLDER, 'debug')
DEBUG_LOG = os.path.join(DEBUG_DIR, 'debug_logs.jsonl')
if DEBUG_MODE:
    os.makedirs(DEBUG_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Disease class labels (exactly as trained)
class_labels = [
    'Bacterial_spot', 'Early_blight', 'Late_blight',
    'Leaf_Mold', 'Septoria_leaf_spot', 'Spider_mites',
    'Target_Spot', 'Yellow_Leaf_Curl_Virus',
    'Mosaic_virus', 'Healthy'
]

# Global ONNX session (loaded once at startup)
session = None
input_name = None

def load_model():
    """Load ONNX model at startup."""
    global session, input_name
    logger.info("="*50)
    logger.info(f"Loading model from: {MODEL_PATH}")
    logger.info(f"File exists: {os.path.exists(MODEL_PATH)}")
    if os.path.exists(MODEL_PATH):
        size = os.path.getsize(MODEL_PATH)/1024/1024
        logger.info(f"File size: {size:.1f} MB")
    logger.info("="*50)

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}\n"
            "Model should have been downloaded during build step.\n"
            "Check build logs for download errors."
        )

    session = ort.InferenceSession(
        MODEL_PATH,
        providers=['CPUExecutionProvider']
    )
    input_name = session.get_inputs()[0].name
    logger.info("Model loaded successfully!")

# Load model at startup
load_model()

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_bytes):
    """Preprocess image for model input (224x224)."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((224, 224))
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, axis=0)
        return arr
    except Exception as e:
        logger.error(f"Image preprocessing error: {e}")
        raise

def is_leaf(image_bytes):
    """Check if image contains a tomato leaf using HSV heuristic."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,
            (GREEN_H_MIN, S_MIN, V_MIN),
            (GREEN_H_MAX, 255, 255))
        
        green_prop = np.sum(mask > 0) / mask.size
        return green_prop >= GREEN_PROP_THRESH
    except Exception as e:
        logger.error(f"Leaf detection error: {e}")
        return False

def generate_mask(image_bytes):
    """Generate green mask overlay as base64 PNG."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,
            (GREEN_H_MIN, S_MIN, V_MIN),
            (GREEN_H_MAX, 255, 255))
        
        green = cv2.bitwise_and(img, img, mask=mask)
        _, buf = cv2.imencode('.png', green)
        return base64.b64encode(buf).decode('utf-8')
    except Exception as e:
        logger.error(f"Mask generation error: {e}")
        return None

def run_prediction(image_bytes):
    """Run model prediction on image bytes."""
    try:
        arr = preprocess_image(image_bytes)
        outputs = session.run(None, {input_name: arr})
        probs = outputs[0][0]
        idx = int(np.argmax(probs))
        confidence = float(probs[idx])
        label = class_labels[idx] if confidence >= CONF_THRESH else 'Uncertain'
        return label, confidence, probs.tolist()
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'model': 'loaded',
        'version': '1.0.0'
    })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Mobile API endpoint: accepts image file and returns JSON prediction."""
    try:
        if 'file' not in request.files:
            logger.warning(f"No file in request. Files: {list(request.files.keys())}")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            logger.warning("File has empty filename")
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            logger.warning(f"File {file.filename} has disallowed extension")
            return jsonify({'error': 'Invalid file type. Allowed: png,jpg,jpeg'}), 400

        # Read file bytes
        image_bytes = file.read()
        filename = secure_filename(file.filename)

        # Leaf check
        if not is_leaf(image_bytes):
            return jsonify({'error': 'Image does not appear to contain a tomato leaf'}), 400

        # Run prediction
        label, confidence, all_probs = run_prediction(image_bytes)

        # Log if debug enabled
        if DEBUG_MODE:
            try:
                debug_entry = {
                    'endpoint': 'api/predict',
                    'filename': filename,
                    'prediction': label,
                    'confidence': round(confidence, 4),
                    'raw_predictions': all_probs
                }
                with open(DEBUG_LOG, 'a', encoding='utf-8') as df:
                    df.write(json.dumps(debug_entry) + '\n')
            except Exception as e:
                logger.info(f"Failed to write debug log: {e}")

        # Generate mask
        mask_b64 = generate_mask(image_bytes)

        logger.info(f"Prediction: {label} ({confidence:.4f})")
        return jsonify({
            'filename': filename,
            'prediction': label,
            'confidence': round(confidence, 4),
            'mask': mask_b64,
            'all_predictions': {class_labels[i]: round(prob, 4) for i, prob in enumerate(all_probs)}
        })

    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Web UI endpoint: accepts form upload and renders result."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('tomato-disease-organic.html', error='No file selected')

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return render_template('tomato-disease-organic.html', error='Invalid file. Please upload PNG, JPG, or JPEG.')

        try:
            # Read file bytes
            image_bytes = file.read()
            filename = secure_filename(file.filename)

            # Save to uploads folder
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            # Leaf check
            if not is_leaf(image_bytes):
                try:
                    os.remove(filepath)
                except:
                    pass
                return render_template('tomato-disease-organic.html', error='Image does not appear to contain a tomato leaf.')

            # Run prediction
            label, confidence, all_probs = run_prediction(image_bytes)

            # Log if debug enabled
            if DEBUG_MODE:
                try:
                    debug_entry = {
                        'endpoint': 'web/upload',
                        'filename': filename,
                        'prediction': label,
                        'confidence': round(confidence, 4),
                        'raw_predictions': all_probs
                    }
                    with open(DEBUG_LOG, 'a', encoding='utf-8') as df:
                        df.write(json.dumps(debug_entry) + '\n')
                except Exception as e:
                    logger.info(f"Failed to write debug log: {e}")

            logger.info(f"Web prediction: {label} ({confidence:.4f})")
            return render_template('tomato-disease-organic.html',
                                 filename=filename,
                                 prediction=label,
                                 confidence=f"{confidence*100:.2f}%")

        except Exception as e:
            logger.error(f"Web upload error: {str(e)}", exc_info=True)
            return render_template('tomato-disease-organic.html', error=f'Error: {str(e)}')

    return render_template('tomato-disease-organic.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    """Admin UI for threshold configuration."""
    if request.method == 'POST':
        try:
            global GREEN_H_MIN, GREEN_H_MAX, S_MIN, V_MIN, GREEN_PROP_THRESH
            GREEN_H_MIN = int(request.form.get('GREEN_H_MIN', GREEN_H_MIN))
            GREEN_H_MAX = int(request.form.get('GREEN_H_MAX', GREEN_H_MAX))
            S_MIN = int(request.form.get('S_MIN', S_MIN))
            V_MIN = int(request.form.get('V_MIN', V_MIN))
            GREEN_PROP_THRESH = float(request.form.get('GREEN_PROP_THRESH', GREEN_PROP_THRESH))
            return render_template('admin.html',
                                 success='Settings updated',
                                 GREEN_H_MIN=GREEN_H_MIN,
                                 GREEN_H_MAX=GREEN_H_MAX,
                                 S_MIN=S_MIN,
                                 V_MIN=V_MIN,
                                 GREEN_PROP_THRESH=GREEN_PROP_THRESH)
        except Exception as e:
            return render_template('admin.html', error=str(e),
                                 GREEN_H_MIN=GREEN_H_MIN,
                                 GREEN_H_MAX=GREEN_H_MAX,
                                 S_MIN=S_MIN,
                                 V_MIN=V_MIN,
                                 GREEN_PROP_THRESH=GREEN_PROP_THRESH)

    return render_template('admin.html',
                         GREEN_H_MIN=GREEN_H_MIN,
                         GREEN_H_MAX=GREEN_H_MAX,
                         S_MIN=S_MIN,
                         V_MIN=V_MIN,
                         GREEN_PROP_THRESH=GREEN_PROP_THRESH)

@app.route('/api/admin/config', methods=['GET', 'POST'])
def admin_api():
    """API endpoint for getting/setting configuration."""
    global GREEN_H_MIN, GREEN_H_MAX, S_MIN, V_MIN, GREEN_PROP_THRESH
    
    if request.method == 'GET':
        return jsonify({
            'GREEN_H_MIN': GREEN_H_MIN,
            'GREEN_H_MAX': GREEN_H_MAX,
            'S_MIN': S_MIN,
            'V_MIN': V_MIN,
            'GREEN_PROP_THRESH': GREEN_PROP_THRESH
        })

    try:
        data = request.get_json(force=True)
        GREEN_H_MIN = int(data.get('GREEN_H_MIN', GREEN_H_MIN))
        GREEN_H_MAX = int(data.get('GREEN_H_MAX', GREEN_H_MAX))
        S_MIN = int(data.get('S_MIN', S_MIN))
        V_MIN = int(data.get('V_MIN', V_MIN))
        GREEN_PROP_THRESH = float(data.get('GREEN_PROP_THRESH', GREEN_PROP_THRESH))
        
        return jsonify({
            'status': 'ok',
            'GREEN_H_MIN': GREEN_H_MIN,
            'GREEN_H_MAX': GREEN_H_MAX,
            'S_MIN': S_MIN,
            'V_MIN': V_MIN,
            'GREEN_PROP_THRESH': GREEN_PROP_THRESH
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Tomato Disease Identification API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
