"""
Run this once locally to generate PWA icons:
python generate_icons.py
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import os

def generate_icon(size, output_path):
    """Generate a simple SpeedReader icon."""
    img  = Image.new('RGB', (size, size), color='#2c2416')
    draw = ImageDraw.Draw(img)

    # draw a golden circle
    margin = size // 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='#c9a84c'
    )

    # draw dark inner circle
    inner_margin = size // 4
    draw.ellipse(
        [inner_margin, inner_margin,
         size - inner_margin, size - inner_margin],
        fill='#2c2416'
    )

    # draw "SR" text
    try:
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = "SR"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2
    y = (size - text_h) // 2

    draw.text((x, y), text, fill='#c9a84c', font=font)
    img.save(output_path, 'PNG')
    print(f"✓ Generated {output_path}")


if __name__ == '__main__':
    if not PIL_AVAILABLE:
        print("Installing Pillow...")
        os.system("pip install Pillow")
        from PIL import Image, ImageDraw, ImageFont

    os.makedirs('speedreading/static/icons', exist_ok=True)
    generate_icon(192, 'speedreading/static/icons/icon-192.png')
    generate_icon(512, 'speedreading/static/icons/icon-512.png')
    print("All icons generated!")