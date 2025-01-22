from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
import mediapipe as mp
import urllib.request
import tempfile
import os

app = Flask(__name__)

# Initialize Mediapipe for segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

def download_image(url):
    try:
        response = urllib.request.urlopen(url)
        image_data = np.asarray(bytearray(response.read()), dtype="uint8")
        return cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    except Exception as e:
        raise ValueError(f"Error downloading image: {e}")

def blur_background(image):
    # Get the segmentation mask
    results = mp_selfie_segmentation.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    mask = results.segmentation_mask

    # Create a blurred background
    blurred_image = cv2.GaussianBlur(image, (55, 55), 0)

    # Normalize the mask and apply it
    mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    output_image = image * mask + blurred_image * (1 - mask)

    return np.uint8(output_image)

@app.route('/blur-background', methods=['POST'])
def process_image():
    data = request.json
    image_url = data.get('image_url')

    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    try:
        # Download the image
        image = download_image(image_url)

        # Blur the background
        processed_image = blur_background(image)

        # Save the processed image to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        cv2.imwrite(temp_file.name, processed_image)

        # Send the processed image back
        return send_file(temp_file.name, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'temp_file' in locals():
            os.unlink(temp_file.name)

if __name__ == '__main__':
    # Use Railway's port if available, else default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
