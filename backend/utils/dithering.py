import numpy as np
from PIL import Image

def floyd_steinberg_dither(image: Image.Image, bit_depth: int):
    """
    Apply Floyd-Steinberg dithering to a grayscale image.
    bit_depth: 1, 2, 4, or 8
    """
    # Ensure grayscale
    img = image.convert('L')
    pixels = np.array(img, dtype=float)
    
    height, width = pixels.shape
    
    # Calculate levels
    # 1-bit: 2 levels (0, 255)
    # 2-bit: 4 levels (0, 85, 170, 255)
    # 4-bit: 16 levels (0, 17, ..., 255)
    # 8-bit: 256 levels (0, 1, ..., 255)
    
    num_levels = 2**bit_depth
    if num_levels > 256:
        num_levels = 256
        
    levels = np.linspace(0, 255, num_levels)
    
    def find_closest_level(pixel_value):
        idx = np.abs(levels - pixel_value).argmin()
        return levels[idx]

    for y in range(height):
        for x in range(width):
            old_val = pixels[y, x]
            new_val = find_closest_level(old_val)
            pixels[y, x] = new_val
            err = old_val - new_val
            
            if x + 1 < width:
                pixels[y, x + 1] += err * 7 / 16
            if y + 1 < height:
                if x > 0:
                    pixels[y + 1, x - 1] += err * 3 / 16
                pixels[y + 1, x] += err * 5 / 16
                if x + 1 < width:
                    pixels[y + 1, x + 1] += err * 1 / 16
                    
    # Clip and convert back to uint8
    pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    result_img = Image.fromarray(pixels, mode='L')
    
    if bit_depth == 1:
        return result_img.convert('1')
    elif bit_depth == 2:
        # PIL doesn't have a native 2-bit mode, we save as 8-bit with limited palette or just P mode
        return result_img.convert('P', palette=Image.ADAPTIVE, colors=4)
    elif bit_depth == 4:
        return result_img.convert('P', palette=Image.ADAPTIVE, colors=16)
    else:
        return result_img
