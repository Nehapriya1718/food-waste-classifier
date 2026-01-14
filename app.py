from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from functools import wraps

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your-secret-key-change-this-in-production-12345'

MODEL_PATH = 'efficientnet_foodwaste.h5'
USERS_FILE = 'users.json'
model = None

if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

def load_classification_model():
    global model
    try:
        model = load_model(MODEL_PATH, compile=False)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise e

load_classification_model()

CLASS_LABELS = ['Organic', 'Recyclable']

WASTE_INFO = {
    'Organic': {
        'description': 'This waste is compostable and can decompose naturally.',
        'disposal': 'Place in green/brown composting bin',
        'examples': 'Food scraps, fruit peels, vegetable waste, coffee grounds',
        'environmental_impact': 'Creates nutrient-rich compost, reduces landfill methane emissions',
        'color': '#4CAF50'
    },
    'Recyclable': {
        'description': 'This material can be processed and reused.',
        'disposal': 'Place in blue recycling bin after cleaning',
        'examples': 'Plastic containers, glass bottles, aluminum cans, paper packaging',
        'environmental_impact': 'Conserves natural resources, reduces energy consumption',
        'color': '#2196F3'
    }
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def preprocess_image(img):
    img = img.resize((260, 260))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def classify_image(img):
    try:
        processed_img = preprocess_image(img)
        predictions = model.predict(processed_img, verbose=0)
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx]) * 100
        predicted_class = CLASS_LABELS[class_idx]
        
        organic_conf = float(predictions[0][0]) * 100
        recyclable_conf = float(predictions[0][1]) * 100
        confidence_diff = abs(organic_conf - recyclable_conf)
        
        MIN_CONFIDENCE = 92
        MIN_DIFFERENCE = 25
        
        print(f"DEBUG - Organic: {organic_conf:.1f}%, Recyclable: {recyclable_conf:.1f}%, Diff: {confidence_diff:.1f}%")
        
        if confidence < MIN_CONFIDENCE:
            print(f"REJECTED - Low confidence: {confidence:.1f}%")
            return {
                'error': 'not_waste',
                'message': f'This does not appear to be a waste item (confidence: {round(confidence, 1)}%). Please upload an image of food waste, recyclable materials, or compostable items only.',
                'confidence': f'{round(confidence, 1)}%'
            }
        
        if confidence_diff < MIN_DIFFERENCE:
            print(f"REJECTED - Predictions too similar (diff: {confidence_diff:.1f}%)")
            return {
                'error': 'not_waste',
                'message': f'Unable to confidently classify this image. This does not appear to be a waste item. Please upload food waste, recyclable materials, or compostable items only.',
                'confidence': f'Organic: {round(organic_conf, 1)}%, Recyclable: {round(recyclable_conf, 1)}%'
            }
        
        print(f"ACCEPTED - {predicted_class} at {confidence:.1f}%")
        return {
            'class': predicted_class,
            'confidence': round(confidence, 2),
            'all_predictions': {
                CLASS_LABELS[i]: round(float(predictions[0][i]) * 100, 2) 
                for i in range(len(CLASS_LABELS))
            }
        }
    except Exception as e:
        print(f"Classification error: {e}")
        return None

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    users = load_users()
    
    if email in users and check_password_hash(users[email]['password'], password):
        session['user'] = email
        session['username'] = users[email]['username']
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    users = load_users()
    
    if email in users:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    users[email] = {
        'username': username,
        'password': generate_password_hash(password),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_users(users)
    session['user'] = email
    session['username'] = username
    return jsonify({'success': True, 'message': 'Account created successfully'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', username=session.get('username'))

@app.route('/classify/upload')
@login_required
def upload_page():
    return render_template('upload.html', username=session.get('username'))

@app.route('/classify/camera')
@login_required
def camera():
    return render_template('camera.html', username=session.get('username'))

# ========== ADDED: Route aliases for navigation buttons ==========
@app.route('/upload')
@login_required
def upload_alias():
    """Alias for upload page - called by navigation buttons"""
    return redirect(url_for('upload_page'))

@app.route('/camera')
@login_required
def camera_alias():
    """Alias for camera page - called by navigation buttons"""
    return redirect(url_for('camera'))

# ========== MODIFIED: Result page handles both session data and URL parameters ==========
@app.route('/result')
@login_required
def result_page():
    """Result page - handles both session data and URL parameters"""
    # Check if data is in URL parameters (from navigation buttons)
    category = request.args.get('category')
    
    if category:
        # Data from URL parameters (direct navigation)
        return render_template('result.html',
                             username=session.get('username'),
                             category=category,
                             confidence=request.args.get('confidence', '0'),
                             disposal=request.args.get('disposal', ''),
                             organic_score=request.args.get('organic_score', '0'),
                             recyclable_score=request.args.get('recyclable_score', '0'))
    
    # Data from session (your existing classification flow)
    result_data = session.get('last_result')
    if not result_data:
        return redirect(url_for('dashboard'))
    return render_template('result.html', username=session.get('username'), result=result_data)

@app.route('/error')
@login_required
def error_page():
    error_data = session.get('last_error')
    if not error_data:
        return redirect(url_for('dashboard'))
    
    session.pop('last_error', None)
    
    return render_template('error.html', 
                         username=session.get('username'),
                         error_message=error_data.get('message'),
                         confidence=error_data.get('confidence'))

@app.route('/api/classify', methods=['POST'])
@login_required
def api_classify():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        result = classify_image(img)
        
        if result and 'error' in result and result['error'] == 'not_waste':
            session['last_error'] = {
                'message': result['message'],
                'confidence': result.get('confidence')
            }
            session.modified = True
            return jsonify({'redirect': '/error'})
        
        if result is None:
            return jsonify({'error': 'Classification failed'}), 500
        
        result['info'] = WASTE_INFO[result['class']]
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['last_result'] = result
        session.modified = True
        
        return jsonify(result)
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/classify/camera', methods=['POST'])
@login_required
def api_classify_camera():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image data'}), 400
        
        image_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        result = classify_image(img)
        
        if result and 'error' in result and result['error'] == 'not_waste':
            session['last_error'] = {
                'message': result['message'],
                'confidence': result.get('confidence')
            }
            session.modified = True
            return jsonify({'redirect': '/error'})
        
        if result is None:
            return jsonify({'error': 'Classification failed'}), 500
        
        result['info'] = WASTE_INFO[result['class']]
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['last_result'] = result
        session.modified = True
        
        return jsonify(result)
    except Exception as e:
        print(f"Camera prediction error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
