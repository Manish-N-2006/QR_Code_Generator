from flask import render_template, Flask,request,url_for, send_file
import os
import qrcode
from io import BytesIO
import base64
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret")
)

@app.route("/")

def index():
    return render_template("index.html")

@app.route("/generate",methods=['POST'])
def generate_qr():
    qr_type = request.form.get("type")
    img_str = ""

    if qr_type == "image":
        file = request.files.get("file")
        if not file:
            return "No file uploaded", 400
        
        upload_result = cloudinary.uploader.upload(file)
        file_url = upload_result["secure_url"]        
        data = file_url

    else:
        data = request.form.get("data")
        if not data:
            return "No data provided", 400
    qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_M,
                   box_size=10, border=4)

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black",back_color="white").convert('RGB')
    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG')
    img_buffer.seek(0)
    last_qr_image = img_buffer.getvalue()
    img_str = base64.b64encode(last_qr_image).decode()

    return render_template("next.html",img_str=img_str,data=data)

@app.route("/download")
def download_qr():
    global last_qr_image
    if not last_qr_image:
        return "No QR code generated yet.", 400

    return send_file(
        BytesIO(last_qr_image),
        mimetype='image/png',          
        as_attachment=True,
        download_name='qrcode.png'     
    )


if __name__ == '__main__':
    app.run(debug=True)
