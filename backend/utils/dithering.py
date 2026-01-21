import numpy as np
from PIL import Image

def floyd_steinberg_dither(image: Image.Image, bit_depth: int, noise_intensity: float = 0.0):
    """
    Apply Floyd-Steinberg dithering to a grayscale image.
    Optimized version using Pillow's native C implementation.
    """
    # 1. Ensure we start with a high-quality grayscale image
    img = image.convert('L')
    
    # 2. Add noise if requested (Vectorized with NumPy, so it's fast)
    if noise_intensity > 0:
        pixels = np.array(img, dtype=float)
        # Scale intensity: 0.1 -> +/- ~25 units of gray
        noise = (np.random.random(pixels.shape) - 0.5) * 2 * (noise_intensity * 255 * 0.5)
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)

    # 3. Apply Floyd-Steinberg Dithering using PIL's optimized C core
    # This is 100x faster than a Python for-loop
    num_colors = 2**bit_depth
    
    if bit_depth == 1:
        # Native 1-bit dithering
        return img.convert('1', dither=Image.FLOYDSTEINBERG)
    
    elif bit_depth <= 4:
        # For 2-bit and 4-bit, we use a Quantized Palette mode
        # Image.FLOYDSTEINBERG constant is used for the dither argument
        return img.convert('P', palette=Image.ADAPTIVE, colors=num_colors, dither=Image.FLOYDSTEINBERG)
    
    else:
        # For 8-bit, if the user wants it "tramado" but in 8-bit, 
        # we can quantize to 256 levels (which is almost nothing) 
        # or just return the noisy L image if no reduction is needed.
        return img.convert('L')
