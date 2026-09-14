import io

from PIL import Image


def extract_dominant_colors(image_bytes: bytes, count: int = 2) -> list[str]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    quantized = image.quantize(colors=max(count, 8), method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    color_counts = sorted(quantized.getcolors(), key=lambda item: item[0], reverse=True)

    colors = []
    for _, index in color_counts[:count]:
        r, g, b = palette[index * 3], palette[index * 3 + 1], palette[index * 3 + 2]
        colors.append(f"#{r:02x}{g:02x}{b:02x}")
    return colors
