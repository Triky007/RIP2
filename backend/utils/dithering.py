import numpy as np
from PIL import Image
import warnings

# Disable transparency/decompression warnings for RIP tasks
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

def floyd_steinberg_dither(image: Image.Image, bit_depth: int, noise_intensity: float = 0.0):
    """
    Apply Floyd-Steinberg dithering to a grayscale image.
    Optimized version with FIXED palettes to ensure visible stochastic patterns.
    """
    # 1. Ensure we start with a high-quality grayscale image
    img = image.convert('L')
    
    # 2. Add noise if requested
    if noise_intensity > 0:
        pixels = np.array(img, dtype=float)
        # Factor calibrated for visible structural break
        noise = (np.random.random(pixels.shape) - 0.5) * 2 * (noise_intensity * 255 * 0.4)
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)

    # 3. Apply Dithering
    num_levels = 2**bit_depth
    if num_levels > 256: num_levels = 256

    if bit_depth == 1:
        # Native 1-bit is always fixed (Black/White)
        return img.convert('1', dither=Image.FLOYDSTEINBERG)
    
    else:
        # Create a FIXED linear grayscale palette
        # This is CRUCIAL: if the palette is adaptive, dithering might disappear
        levels = np.linspace(0, 255, num_levels).astype(np.uint8)
        
        # PIL Palette: list of 768 values [R,G,B, R,G,B, ...]
        palette = []
        for v in levels:
            palette.extend([v, v, v])
        
        # Pad palette up to 256 colors (768 entries)
        padding = [0] * (768 - len(palette))
        palette.extend(padding)
        
        # Create a template image with this specific palette
        pal_img = Image.new('P', (1, 1))
        pal_img.putpalette(palette)
        
        # Quantize using our fixed palette and Floyd-Steinberg
        # This forces the "dots" because it must interpolate between the fixed gray levels
        return img.quantize(colors=num_levels, palette=pal_img, dither=Image.FLOYDSTEINBERG).convert('P')
