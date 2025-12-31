from flask import render_template, Flask,request,url_for, send_file
import os
import qrcode
from io import BytesIO
import base64
import cloudinary
import cloudinary.uploader
import threading
import time
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
last_qr_image = None

cloudinary.config(
    cloud_name=os.getenv(cloud_name),
    api_key=os.getenv(api_key),
    api_secret=os.get(api_secret)"
)


def auto_delete_file(public_id, delay_seconds=86400,resource_type = "raw"):
    def delete():
        time.sleep(delay_seconds)
        cloudinary.uploader.destroy(public_id,resource_type=resource_type)
    threading.Thread(target=delete,daemon=True).start()

@app.route("/")

def index():
    return render_template("index.html")

@app.route("/generate",methods=['POST'])
def generate_qr():
    global last_qr_image
    qr_type = request.form.get("type")
    img_str = ""

    if qr_type == "image" or qr_type == "file":
        file = request.files.get("file")
        if not file:
            return "No file uploaded", 400
        mime_type = file.mimetype
        if mime_type.startswith("image/"):
            res_type = "image"
        elif mime_type.startswith("video/"):
            res_type = "video"
        else:
            res_type = "auto" 
            
        upload_result = cloudinary.uploader.upload(file, resource_type = res_type)
        file_url = upload_result["secure_url"] 

        if res_type == "auto" and not (mime_type.startswith("image/") or mime_type.startswith("video/")):
            file_url += "?attachment=true"

        public_id = upload_result["public_id"]
        data = file_url
        auto_delete_file(public_id,resource_type = res_type)

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
