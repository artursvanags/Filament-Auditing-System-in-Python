import os
import qrcode

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont 

def generate_qr_label(token, data):  
    date = datetime.today().strftime('%Y-%m-%d')
    # Set QR code size
    qr_size = 300
    qr_size_width = qr_size + 350
    # Create QR code from token
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((qr_size, qr_size))

    # Create image and set its size
    image = Image.new("RGB", (qr_size_width, qr_size), color='white')
    draw = ImageDraw.Draw(image)

    # Add QR code to the image
    image.paste(img, (0, 0))

    # Add text to the image
    token_font = ImageFont.truetype("arialbd.ttf", 34)
    data_font  = ImageFont.truetype("arial.ttf", 34)
    brand_font = ImageFont.truetype("arial.ttf", 24)

    draw.text((qr_size, 20), f"{token}\n{date}", fill="black", font=token_font)
    draw.text((qr_size, 100), data, fill="black", font=data_font)
    draw.text((qr_size, qr_size*0.83), "printscopia.com", fill="black", font=brand_font)
    # Save image to disk
    if not os.path.exists("qr"):
        os.mkdir("qr")
    image.save(f"qr/{token}.png")