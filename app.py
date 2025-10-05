from flask import Flask, jsonify, request,render_template
import qrcode
from flask_cors import CORS
import datetime
from datetime import date
import io
import os
import base64

app=Flask(__name__)
CORS(app) # Enable CORS for all routes
@app.route('/',methods=['GET'])
def index():
    print("Request for index page received")
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@app.route('/generate', methods=['POST'])
def generate_qr():
    try:
        vendorName = request.form.get('vendorName')
        componentName = request.form.get('componentName')
        vendorArea = request.form.get('vendorArea')
        componentQuantity = request.form.get('componentQuantity')
        
        print(f"Vendor: {vendorName}, Component: {componentName}")
        
        if not vendorName or not componentName:
            return jsonify({'error': 'Missing vendor or component name'}), 400
        
        vendorCap = vendorName.capitalize()
        componentCap = componentName.capitalize()
        vend_ = vendorCap[0:2].upper()
        comp_ = componentCap[0:2].upper()
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        data = vend_ + comp_ + now
        
        # Generate QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        # Save to BytesIO buffer FIRST (before saving to file)
        buf = io.BytesIO()
        img.save(buf, format='PNG')  # Important: specify format
        buf.seek(0)
        
        # Save to file
        filename = f"{vendorName}_{componentName}_{now}.png"
        upload_dir = os.path.join(app.root_path, "upload")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)  # Use makedirs instead of mkdir for better error handling
            print(f"Created directory: {upload_dir}")
        
        filepath = os.path.join(upload_dir, filename)
        img.save(filepath)
        print(f"Saved QR code to: {filepath}")
        
        # Convert buffer to base64
        img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")  # Use getvalue() instead of read()
        data_url = f"data:image/png;base64,{img_b64}"
        
        # Return JSON response with image
        return jsonify({
            'success': True,
            'unique_id': data,
            'qr_image': data_url,  # This sends the image to frontend
            'filename': filename,
            'filepath': filepath,
            'vendor': vendorName,
            'component': componentName,
            'quantity': componentQuantity,
            'area': vendorArea
        }), 200
        
    except Exception as e:
        print(f"Error in generate_qr: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("Running app...")
    app.run(debug=True)