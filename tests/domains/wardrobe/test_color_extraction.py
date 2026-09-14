import io

from PIL import Image

from app.domains.wardrobe.color_extraction import extract_dominant_colors


def _solid_image_bytes(color: tuple[int, int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(buffer, format="PNG")
    return buffer.getvalue()


def test_extracts_the_dominant_color_of_a_solid_image():
    colors = extract_dominant_colors(_solid_image_bytes((255, 0, 0)), count=1)
    assert colors == ["#ff0000"]


def _two_tone_image_bytes(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> bytes:
    image = Image.new("RGB", (32, 32), top)
    for y in range(16, 32):
        for x in range(32):
            image.putpixel((x, y), bottom)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_returns_the_requested_number_of_colors():
    colors = extract_dominant_colors(_two_tone_image_bytes((0, 255, 0), (0, 0, 255)), count=2)
    assert len(colors) == 2
    assert all(c.startswith("#") and len(c) == 7 for c in colors)
