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
    # IMPORTANT: Don't add noise to pure whites or pure blacks to avoid stray dots
    if noise_intensity > 0:
        pixels = np.array(img, dtype=float)
        # Scale intensity: 0.1 -> +/- ~25 units of gray
        noise = (np.random.random(pixels.shape) - 0.5) * 2 * (noise_intensity * 255 * 0.5)
        
        # Create a mask for extreme values (near white or near black)
        # Don't apply noise to very light (>250) or very dark (<5) areas
        safe_zone = (pixels > 5) & (pixels < 250)
        
        # Only apply noise where it's safe
        pixels = np.where(safe_zone, pixels + noise, pixels)
        pixels = np.clip(pixels, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)

    # 3. Apply Floyd-Steinberg Dithering
    num_colors = 2**bit_depth
    if num_colors > 256:
        num_colors = 256
    
    if bit_depth == 1:
        # Native 1-bit dithering (best performance)
        return img.convert('1', dither=Image.FLOYDSTEINBERG)
    
    # For 2, 4, 8-bit: Create a grayscale palette and use quantize()
    # This forces PIL to apply error diffusion to the limited levels
    
    # Create grayscale palette: e.g. for 4 colors: [0, 85, 170, 255]
    palette_data = []
    for i in range(num_colors):
        gray_val = int(i * 255 / (num_colors - 1)) if num_colors > 1 else 0
        palette_data.extend([gray_val, gray_val, gray_val])  # R=G=B for grayscale
    
    # Pad palette to 256 colors (768 bytes = 256 * 3)
    palette_data.extend([0] * (768 - len(palette_data)))
    
    # Create a tiny palette image to use as reference
    pal_img = Image.new('P', (1, 1))
    pal_img.putpalette(palette_data)
    
    # Convert L to RGB first (quantize needs RGB or L, but palette ref needs RGB-ish behavior)
    rgb_img = img.convert('RGB')
    
    # Quantize with dither=1 (Floyd-Steinberg)
    dithered = rgb_img.quantize(palette=pal_img, dither=1)
    
    return dithered
