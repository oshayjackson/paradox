from flask import Flask, jsonify, request, render_template
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_apod')
def get_apod():
    try:
        # User date params
        selected_date = request.args.get('date', '')

        # Log the received date for debugging
        print('Received Date:', selected_date)

        # [Today] is default when no arguments are passed
        if not selected_date:
            import datetime
            selected_date = datetime.date.today().strftime('%Y-%m-%d')

        api_key = 'dghzcymYwwekvkWX8HF91sAvjbu6Vu2vu8TxYoQt'
        url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}&date={selected_date}'

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # API response for debugging
        print('API Response:', data)

        # Generate HD image URL (if 'hdurl' is present)
        hd_url = data.get('hdurl')
        hd_image_url = None

        if hd_url:
            hd_image_url = generate_hd_image_url(hd_url, selected_date)

        return jsonify({
            'title': data.get('title'),
            'date': data.get('date'),
            'copyright': data.get('copyright'),
            'explanation': data.get('explanation'),
            'hd_image_url': hd_image_url,
            'url': data.get('url')
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching APOD: {str(e)}'})

def generate_hd_image_url(hd_url, filename):
    try:
        # Download HD image
        hd_image_response = requests.get(hd_url)
        hd_image_response.raise_for_status()

        # Open the image using Pillow
        hd_image = Image.open(BytesIO(hd_image_response.content))

        # Resize the image to HD dimensions (customize as needed)
        hd_image_resized = hd_image.resize((1920, 1080))

        # Convert the resized image to bytes
        hd_image_bytes = BytesIO()
        hd_image_resized.save(hd_image_bytes, format='JPEG')

        # Generate a data URL for the resized image
        hd_image_url = f'data:image/jpeg;base64,{hd_image_bytes.getvalue().decode("latin-1")}'  # Use 'latin-1' encoding
        return hd_image_url

    except Exception as e:
        print(f'Error generating HD image URL: {str(e)}')
        return None

if __name__ == '__main__':
    app.run(debug=True)
