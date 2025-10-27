# shortener/identicon_utils.py
import hashlib
from PIL import Image, ImageDraw
from io import BytesIO


def generate_identicon(text, size=5, pixel_size=50):
    """
    Generate an identicon based on input text.

    Args:
        text: String to generate identicon from
        size: Grid size (default 5x5)
        pixel_size: Size of each pixel in the grid

    Returns:
        PIL Image object
    """
    # Generate hash from text
    hash_value = hashlib.md5(text.encode()).hexdigest()

    # Convert hash to binary
    binary = bin(int(hash_value, 16))[2:].zfill(128)

    # Extract color from first 6 hex characters
    color = tuple(int(hash_value[i:i + 2], 16) for i in (0, 2, 4))

    # Create image
    img_size = size * pixel_size
    img = Image.new('RGB', (img_size, img_size), 'white')
    draw = ImageDraw.Draw(img)

    # Generate symmetric pattern (mirror horizontally)
    half = size // 2
    for row in range(size):
        for col in range(half + 1):
            idx = row * (half + 1) + col
            if idx < len(binary) and binary[idx] == '1':
                # Draw pixel and its mirror
                draw.rectangle(
                    [col * pixel_size, row * pixel_size,
                     (col + 1) * pixel_size, (row + 1) * pixel_size],
                    fill=color
                )
                if col < half:
                    mirror_col = size - col - 1
                    draw.rectangle(
                        [mirror_col * pixel_size, row * pixel_size,
                         (mirror_col + 1) * pixel_size, (row + 1) * pixel_size],
                        fill=color
                    )

    return img


def generate_identicon_response(username):
    """
    Generate an identicon and return it as bytes for HTTP response.

    Args:
        username: Username to generate identicon for

    Returns:
        BytesIO object containing PNG image data
    """
    img = generate_identicon(username)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
