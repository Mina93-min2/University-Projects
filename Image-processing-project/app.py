from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
# Import all required functions from modules
from functions import *
from bonus import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# --- 1. Brightness Route ---
@app.route('/process_brightness', methods=['POST'])
def process_brightness():
    try:
        data = request.json
        value = int(data['value'])
        image_data = data['image'].split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # Safety check: if image fails to decode
        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Apply logic: Add vs Subtract
        if value > 0:
            processed_img = point_add(img, value)
        elif value < 0:
            processed_img = point_subtract(img, abs(value))
        else:
            processed_img = img

        # Ensure proper image encoding
        success, buffer = cv2.imencode('.png', processed_img)
        if not success:
            return jsonify({'error': 'Failed to encode image'}), 500
            
        processed_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'result': 'data:image/png;base64,' + processed_base64})
    
    except Exception as e:
        print(f"Error in Brightness: {e}")
        return jsonify({'error': str(e)}), 500

# --- 2. Multiply/Divide Route ---
@app.route('/process_contrast', methods=['POST'])
def process_contrast():
    try:
        data = request.json
        value = int(data['value'])
        image_data = data['image'].split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None: return jsonify({'error': 'No image'}), 400

        # Multiplication and division logic: right positive = multiply, left negative = divide
        if value > 0:
            # Divide by 10 to prevent large values (if slider is 10, multiply by 2)
            factor = 1 + (value / 10) 
            processed_img = point_multiply(img, factor)
        elif value < 0:
            factor = 1 + (abs(value) / 10)
            processed_img = point_divide(img, factor)
        else:
            processed_img = img

        success, buffer = cv2.imencode('.png', processed_img)
        processed_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'result': 'data:image/png;base64,' + processed_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    





@app.route('/process_complementary', methods=['POST'])
def process_complementary():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None: 
            return jsonify({'error': 'No image'}), 400

        # Call the complementary/invert function
        processed_img = point_complementary(img)

        success, buffer = cv2.imencode('.png', processed_img)
        if not success:
            return jsonify({'error': 'Failed to encode'}), 500
            
        processed_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'result': 'data:image/png;base64,' + processed_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



@app.route('/process_solarization', methods=['POST'])
def process_solarization():
    try:
        data = request.json
        threshold = int(data['threshold'])
        mode = data['mode'] # 'greater' or 'less'
        image_data = data['image'].split(',')[1]
        
        img_bytes = base64.decodebytes(image_data.encode())
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None: return jsonify({'error': 'No image'}), 400

        # Call the unified solarization function
        processed_img = solarization(img, threshold, mode)

        success, buffer = cv2.imencode('.png', processed_img)
        processed_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'result': 'data:image/png;base64,' + processed_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/process_hist_stretch', methods=['POST'])
def process_hist_stretch():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None: 
            return jsonify({'error': 'Failed to decode image'}), 400

        # Call the histogram stretching function
        processed_img = histogram_stretching(img)

        success, buffer = cv2.imencode('.png', processed_img)
        processed_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'result': 'data:image/png;base64,' + processed_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500









@app.route('/get_histogram', methods=['POST'])
def get_histogram():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None: 
            return jsonify({'error': 'No image'}), 400

        # Call compute histogram function
        hist = compute_histogram(img)
        
        # Convert NumPy array to list for JSON serialization
        return jsonify({'histogram': hist.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500








@app.route('/process_addition', methods=['POST'])
def process_addition():
    try:
        data = request.json
        # 1. Decode first and second images
        img1 = decode_image(data['image1'])
        img2 = decode_image(data['image2'])

        if img1 is None or img2 is None:
            return jsonify({'error': 'Missing images'}), 400

        # 2. Call the image addition function
        result_img = control_image_add(img1, img2)

        # 3. Encode result and send to JavaScript
        return jsonify({'result': encode_image(result_img)})
    except Exception as e:
        print(f"Error in Addition: {str(e)}")
        return jsonify({'error': str(e)}), 500




@app.route('/process_subtraction', methods=['POST'])
def process_subtraction():
    try:
        data = request.json
        img1 = decode_image(data['image1'])
        img2 = decode_image(data['image2'])

        if img1 is None or img2 is None:
            return jsonify({'error': 'Images missing'}), 400

        # Call the image subtraction function
        # Uses max(subtract, 0) to prevent negative values
        result_img = control_image_subtract(img1, img2)

        return jsonify({'result': encode_image(result_img)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500





@app.route('/process_blending', methods=['POST'])
def process_blending():
    try:
        data = request.json
        img1 = decode_image(data['image1'])
        img2 = decode_image(data['image2'])
        
        # Receive weight values from JavaScript and convert to float
        alpha = float(data.get('alpha', 0.5))
        beta = float(data.get('beta', 0.5))

        if img1 is None or img2 is None:
            return jsonify({'error': 'Images missing'}), 400

        # Call the image blending function
        result_img = control_image_blend(img1, img2, alpha, beta)

        return jsonify({'result': encode_image(result_img)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/process_mean_filter', methods=['POST'])
def process_mean_filter():
    try:
        data = request.json
        img = decode_image(data['image'])
        
        # Get checkbox state (True/False)
        padding_flag = data.get('padding', True)

        if img is None:
            return jsonify({'error': 'Image not found'}), 400

        # Call the mean filter function
        # It uses np.pad with constant_values=0
        result_img = mean_filter(img, zero_padding=padding_flag)

        return jsonify({'result': encode_image(result_img)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



@app.route('/process_median_filter', methods=['POST'])
def process_median_filter_route():
    try:
        data = request.json
        img = decode_image(data['image'])
        padding_flag = data.get('padding', True)

        if img is None:
            return jsonify({'error': 'Image not found'}), 400

        # Call the median filter function
        result_img = median_filter(img, zero_padding=padding_flag)

        return jsonify({'result': encode_image(result_img)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500





@app.route('/process_min_filter', methods=['POST'])
def process_min_filter_route():
    try:
        data = request.json
        img = decode_image(data['image'])
        padding_flag = data.get('padding', True)

        if img is None:
            return jsonify({'error': 'Image not found'}), 400

        # Call the min filter function
        result_img = min_filter(img, zero_padding=padding_flag)

        return jsonify({'result': encode_image(result_img)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500









@app.route('/process_max_filter', methods=['POST'])
def process_max_filter_route():
    try:
        data = request.json
        img = decode_image(data['image'])
        padding_flag = data.get('padding', True)

        if img is None:
            return jsonify({'error': 'Image not found'}), 400

        # Call the max filter function
        result_img = max_filter(img, zero_padding=padding_flag)

        return jsonify({'result': encode_image(result_img)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    







@app.route('/process_spatial', methods=['POST'])
def process_spatial():
    data = request.json
    img = decode_image(data['image'])
    filter_type = data['filter_type']
    size = data.get('size', 3)
    
    if img is None: return jsonify({'error': 'No image'}), 400

    if filter_type == 'average':
        result = spatial_average_filter(img, filter_size=size)
    elif filter_type == 'gaussian':
        sigma = data.get('sigma', 1.0)
        result = spatial_gaussian_filter(img, filter_size=size, sigma=sigma)
    
    return jsonify({'result': encode_image(result)})





@app.route('/process_noise', methods=['POST'])
def process_noise():
    data = request.json
    img = decode_image(data['image'])
    ratio = data.get('ratio', 0.05)
    
    if img is None: return jsonify({'error': 'No image'}), 400

    # Call the salt and pepper noise function
    noisy_img = add_salt_and_pepper_noise(img, noise_ratio=ratio)
    return jsonify({'result': encode_image(noisy_img)})

@app.route('/calculate_metrics', methods=['POST'])
def calculate_metrics():
    data = request.json
    # Decode both images for comparison
    original = decode_image(data['original'])
    restored = decode_image(data['restored'])
    
    if original is None or restored is None:
        return jsonify({'error': 'Missing images'}), 400

    # Resize to same dimensions for pixel-by-pixel SNR calculation
    if original.shape != restored.shape:
        restored = cv2.resize(restored, (original.shape[1], original.shape[0]))

    # Call the SNR calculation function
    snr_val = calculate_snr(original, restored)
    
    return jsonify({'snr': float(snr_val)})



@app.route('/process_morphology', methods=['POST'])
def process_morphology():
    data = request.json
    img = decode_image(data['image'])
    m_type = data['morph_type']
    size = data.get('size', 5)
    
    if img is None: return jsonify({'error': 'No image'}), 400

    # Execute operation based on UI selection
    if m_type == 'erosion':
        result = morph_erosion(img, size)
    elif m_type == 'dilation':
        result = morph_dilation(img, size)
    elif m_type == 'opening':
        result = morph_opening(img, size)
    elif m_type == 'closing':
        result = morph_closing(img, size)
    
    return jsonify({'result': encode_image(result)})







@app.route('/process_segmentation', methods=['POST'])
def process_segmentation():
    data = request.json
    img = decode_image(data['image'])
    seg_type = data['seg_type']
    
    if img is None: return jsonify({'error': 'No image'}), 400

    if seg_type == 'otsu':
        result = segmentation_otsu(img)
    elif seg_type == 'dithering':
        result = segmentation_dithering(img)
    
    return jsonify({'result': encode_image(result)})





@app.route('/process_bonus', methods=['POST'])
def handle_bonus():
    try:
        data = request.json
        image_data = data.get('image')
        filter_type = data.get('filter_type')

        if not image_data:
            return jsonify({'error': 'No image data found'}), 400

        # Convert image from Base64 to NumPy array
        img = decode_image(image_data)

        # Select appropriate filter based on request
        if filter_type == 'sobel':
            result = bonus_sobel(img)
        elif filter_type == 'hist_eq':
            result = bonus_hist_eq(img)
        elif filter_type == 'adaptive':
            result = bonus_adaptive_thresh(img)
        elif filter_type == 'kmeans':
            result = bonus_kmeans(img, k=3) # K can be made variable if needed
        elif filter_type == 'canny':
            result = bonus_canny(img)
        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        # Convert result to Base64 for UI response
        encoded_result = encode_image(result)
        return jsonify({'result': encoded_result})

    except Exception as e:
        print(f"Bonus Error: {str(e)}")
        return jsonify({'error': str(e)}), 500



























if __name__ == '__main__':
    app.run(debug=True, port=5000)