import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import tensorflow as tf

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MODEL_PATH = 'models/tomato_model.h5'
# Optional leaf-detector model (binary: leaf / not-leaf)
LEAF_DETECTOR_PATH = 'models/leaf_detector.h5'

# Configurable HSV thresholds and green proportion via env (defaults tuned)
GREEN_H_MIN = int(os.getenv('GREEN_H_MIN', 25))
GREEN_H_MAX = int(os.getenv('GREEN_H_MAX', 100))
S_MIN = int(os.getenv('S_MIN', 40))
V_MIN = int(os.getenv('V_MIN', 40))
GREEN_PROP_THRESH = float(os.getenv('GREEN_PROP_THRESH', 0.03))

# Persisted config file for admin-tuned thresholds
CONFIG_PATH = 'config.json'

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            import json
            with open(CONFIG_PATH, 'r') as f:
                cfg = json.load(f)
            return cfg
        except Exception:
            return {}
    return {}

def save_config(cfg):
    try:
        import json
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f)
    except Exception as e:
        print(f"Error saving config: {e}")

# Load persisted overrides (if any)
_cfg = load_config()
GREEN_H_MIN = int(_cfg.get('GREEN_H_MIN', GREEN_H_MIN))
GREEN_H_MAX = int(_cfg.get('GREEN_H_MAX', GREEN_H_MAX))
S_MIN = int(_cfg.get('S_MIN', S_MIN))
V_MIN = int(_cfg.get('V_MIN', V_MIN))
GREEN_PROP_THRESH = float(_cfg.get('GREEN_PROP_THRESH', GREEN_PROP_THRESH))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Disease class labels
class_labels = [
    'Bacterial_spot', 'Early_blight', 'Late_blight',
    'Leaf_Mold', 'Septoria_leaf_spot', 'Spider_mites',
    'Target_Spot', 'Yellow_Leaf_Curl_Virus',
    'Mosaic_virus', 'Healthy'
]

# Load the model (with error handling)
def load_model():
    try:
        # If model is missing but a download URL is provided, try to fetch it
        model_url = os.getenv('MODEL_URL')
        if not os.path.exists(MODEL_PATH) and model_url:
            try:
                import requests
                os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
                resp = requests.get(model_url, stream=True, timeout=60)
                if resp.status_code == 200:
                    with open(MODEL_PATH, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                else:
                    print(f"Failed to download model, status: {resp.status_code}")
            except Exception as e:
                print(f"Error downloading model from MODEL_URL: {e}")

        if not os.path.exists(MODEL_PATH):
            return None
        return tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    # Load and preprocess the image
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = img_array.astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def is_leaf_image(image_path, green_h_min=GREEN_H_MIN, green_h_max=GREEN_H_MAX,
                  s_min=S_MIN, v_min=V_MIN, green_prop_thresh=GREEN_PROP_THRESH):
    """
    Heuristic check whether the image contains a leaf/plant by checking
    the proportion of green pixels in HSV space.

    Parameters:
    - image_path: path to image file
    - green_h_min/green_h_max: H range (0-255) considered green
    - s_min, v_min: minimum saturation/value to count as a colored pixel
    - green_prop_thresh: minimum proportion of green pixels to accept
    """
    try:
        img = Image.open(image_path).convert('HSV')
        arr = np.array(img)
        if arr.size == 0:
            return False
        h = arr[:, :, 0]
        s = arr[:, :, 1]
        v = arr[:, :, 2]

        green_mask = (h >= green_h_min) & (h <= green_h_max) & (s >= s_min) & (v >= v_min)
        green_count = np.count_nonzero(green_mask)
        total_pixels = h.size
        prop = green_count / float(total_pixels)

        return prop >= green_prop_thresh
    except Exception as e:
        print(f"Leaf-detection error: {e}")
        return False


def load_leaf_detector():
    """Lazy-load an optional leaf-detector binary model if present."""
    try:
        if not os.path.exists(LEAF_DETECTOR_PATH):
            return None
        return tf.keras.models.load_model(LEAF_DETECTOR_PATH)
    except Exception as e:
        print(f"Error loading leaf detector: {e}")
        return None


leaf_detector = None


def make_mask_overlay(image_path):
    """Create and save a green-mask overlay PNG next to the uploaded image and return its filename."""
    try:
        img = Image.open(image_path).convert('RGB')
        hsv = img.convert('HSV')
        arr = np.array(hsv)
        h = arr[:, :, 0]
        s = arr[:, :, 1]
        v = arr[:, :, 2]
        mask = (h >= GREEN_H_MIN) & (h <= GREEN_H_MAX) & (s >= S_MIN) & (v >= V_MIN)

        mask_img = Image.fromarray((mask * 255).astype('uint8'))
        mask_img = mask_img.convert('L')

        # Create an RGBA overlay: green where mask true, transparent elsewhere
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        green_layer = Image.new('RGBA', img.size, (0, 255, 0, 120))
        overlay.paste(green_layer, mask=mask_img)

        base = img.convert('RGBA')
        combined = Image.alpha_composite(base, overlay)

        # Save to uploads folder with suffix
        dirname, fname = os.path.split(image_path)
        name, ext = os.path.splitext(fname)
        out_name = f"{name}_mask.png"
        out_path = os.path.join(dirname, out_name)
        combined.save(out_path)
        return out_name
    except Exception as e:
        print(f"Error creating mask overlay: {e}")
        return None

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})


@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    """Simple admin UI to view/update HSV thresholds."""
    global GREEN_H_MIN, GREEN_H_MAX, S_MIN, V_MIN, GREEN_PROP_THRESH
    if request.method == 'POST':
        try:
            GREEN_H_MIN = int(request.form.get('GREEN_H_MIN', GREEN_H_MIN))
            GREEN_H_MAX = int(request.form.get('GREEN_H_MAX', GREEN_H_MAX))
            S_MIN = int(request.form.get('S_MIN', S_MIN))
            V_MIN = int(request.form.get('V_MIN', V_MIN))
            GREEN_PROP_THRESH = float(request.form.get('GREEN_PROP_THRESH', GREEN_PROP_THRESH))
            # persist
            cfg = {
                'GREEN_H_MIN': GREEN_H_MIN,
                'GREEN_H_MAX': GREEN_H_MAX,
                'S_MIN': S_MIN,
                'V_MIN': V_MIN,
                'GREEN_PROP_THRESH': GREEN_PROP_THRESH
            }
            save_config(cfg)
            return render_template('admin.html', success='Saved', **cfg)
        except Exception as e:
            return render_template('admin.html', error=str(e),
                                   GREEN_H_MIN=GREEN_H_MIN, GREEN_H_MAX=GREEN_H_MAX,
                                   S_MIN=S_MIN, V_MIN=V_MIN, GREEN_PROP_THRESH=GREEN_PROP_THRESH)

    return render_template('admin.html', GREEN_H_MIN=GREEN_H_MIN, GREEN_H_MAX=GREEN_H_MAX,
                           S_MIN=S_MIN, V_MIN=V_MIN, GREEN_PROP_THRESH=GREEN_PROP_THRESH)


@app.route('/admin/api', methods=['GET', 'POST'])
def admin_api():
    """JSON API to get or set thresholds. GET returns current values. POST accepts JSON body to update and persist."""
    global GREEN_H_MIN, GREEN_H_MAX, S_MIN, V_MIN, GREEN_PROP_THRESH
    if request.method == 'GET':
        return jsonify({
            'GREEN_H_MIN': GREEN_H_MIN,
            'GREEN_H_MAX': GREEN_H_MAX,
            'S_MIN': S_MIN,
            'V_MIN': V_MIN,
            'GREEN_PROP_THRESH': GREEN_PROP_THRESH
        })

    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'No JSON body provided'}), 400
    try:
        GREEN_H_MIN = int(data.get('GREEN_H_MIN', GREEN_H_MIN))
        GREEN_H_MAX = int(data.get('GREEN_H_MAX', GREEN_H_MAX))
        S_MIN = int(data.get('S_MIN', S_MIN))
        V_MIN = int(data.get('V_MIN', V_MIN))
        GREEN_PROP_THRESH = float(data.get('GREEN_PROP_THRESH', GREEN_PROP_THRESH))
        cfg = {
            'GREEN_H_MIN': GREEN_H_MIN,
            'GREEN_H_MAX': GREEN_H_MAX,
            'S_MIN': S_MIN,
            'V_MIN': V_MIN,
            'GREEN_PROP_THRESH': GREEN_PROP_THRESH
        }
        save_config(cfg)
        return jsonify({'status': 'ok', **cfg})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/preview/<filename>')
def preview(filename):
    """Generate (if needed) and show mask overlay for an uploaded file."""
    uploads = app.config['UPLOAD_FOLDER']
    filepath = os.path.join(uploads, filename)
    if not os.path.exists(filepath):
        return "File not found", 404

    maskname = f"{os.path.splitext(filename)[0]}_mask.png"
    maskpath = os.path.join(uploads, maskname)
    if not os.path.exists(maskpath):
        make_mask_overlay(filepath)

    return render_template('preview.html', filename=filename, maskname=maskname)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # Check if a file was uploaded
        if 'file' not in request.files:
            return render_template('index.html', error='No file selected')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected')

        if file and allowed_file(file.filename):
            try:
                # Save the uploaded file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                
                # Quick leaf/plant check — reject images with too little green
                # Prefer the optional leaf detector model if available
                global leaf_detector
                if leaf_detector is None:
                    leaf_detector = load_leaf_detector()

                if leaf_detector is not None:
                    try:
                        ld_img = Image.open(filepath).convert('RGB').resize((128,128))
                        ld_arr = np.array(ld_img).astype('float32') / 255.0
                        ld_arr = np.expand_dims(ld_arr, axis=0)
                        pred = leaf_detector.predict(ld_arr)[0][0]
                        # leaf_detector outputs probability of leaf (sigmoid)
                        if float(pred) < 0.5:
                            try:
                                os.remove(filepath)
                            except Exception:
                                pass
                            return render_template('index.html', error='Uploaded image does not appear to contain a tomato leaf. Please upload a clear leaf image.')
                    except Exception as e:
                        print(f"Leaf-detector prediction error: {e}")
                        # fallback to heuristic below

                # If no detector or detector couldn't run, fallback to HSV heuristic
                if leaf_detector is None and not is_leaf_image(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                    return render_template('index.html', error='Uploaded image does not appear to contain a tomato leaf. Please upload a clear leaf image.')

                # Preprocess the image
                processed_image = preprocess_image(filepath)

                # Ensure model is loaded (lazy load)
                global model
                if model is None:
                    model = load_model()
                    if model is None:
                        return render_template('index.html', 
                                               error="Model not found. Please place tomato_model.h5 in the models directory.")

                # Make prediction
                predictions = model.predict(processed_image)
                predicted_class = class_labels[np.argmax(predictions[0])]
                confidence = float(np.max(predictions[0]) * 100)

                return render_template('index.html',
                                    filename=filename,
                                    prediction=predicted_class,
                                    confidence=f"{confidence:.2f}%")
            except Exception as e:
                return render_template('index.html', error=f"Error processing image: {str(e)}")
        else:
            return render_template('index.html', 
                                error='Invalid file type. Please upload a JPG, JPEG, or PNG image.')

    return render_template('index.html')

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Check if model exists and print status
    if model is None:
        print("Warning: Model not found. Please place tomato_model.h5 in the models directory.")
    else:
        print("Model loaded successfully!")
    
    app.run(debug=True)