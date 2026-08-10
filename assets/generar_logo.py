"""Genera logo PNG desde SVG (ejecutar una vez si no tienes cairosvg)."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(BASE, "logo_mita.png")
SVG = os.path.join(BASE, "logo_mita.svg")


def generar_fallback():
    size = 256
    img = Image.new("RGBA", (size, size), (249, 248, 244, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, size - 20, size - 20], fill="#628272")
    draw.text((72, 88), "Mi", fill="#21574A")
    draw.text((130, 110), "ta", fill="#F9F8F4")
    img.save(PNG)
    print(f"Logo generado: {PNG}")


if __name__ == "__main__":
    if os.path.exists(SVG):
        try:
            import cairosvg
            cairosvg.svg2png(url=SVG, write_to=PNG, output_width=256, output_height=256)
            print(f"Logo SVG convertido: {PNG}")
        except Exception:
            generar_fallback()
    else:
        generar_fallback()
