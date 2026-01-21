import os
import tempfile
from PIL import Image
from utils.ghostscript import rasterize_pdf
from utils.dithering import floyd_steinberg_dither

# Disable PIL's DecompressionBomb warning as we expect large images for RIP2
Image.MAX_IMAGE_PIXELS = None

def process_pdf_to_rip(pdf_path: str, bit_depth: int, file_type: str, dpi: int | str = 300, noise_level: float = 0.0, threads: int = 8, memory_mb: int = 2000):
    """
    Orchestrates the conversion from PDF to screened image.
    bit_depth: 1, 2, 4, 8
    file_type: 'tiff', 'bmp'
    noise_level: 0.0 to 1.0
    dpi: int or str (e.g., "1200x600")
    threads: int
    memory_mb: int
    """
    
    # Parse DPI
    if isinstance(dpi, str) and 'x' in dpi.lower():
        parts = dpi.lower().split('x')
        parsed_dpi = (int(parts[0]), int(parts[1]))
    else:
        parsed_dpi = int(dpi)

    # 1. Rasterize to grayscale intermediate
    gray_tif = rasterize_pdf(pdf_path, parsed_dpi, threads=threads, memory_mb=memory_mb)
    
    try:
        # 2. Open with PIL
        img = Image.open(gray_tif)
        
        # 3. Apply dithering
        result = floyd_steinberg_dither(img, bit_depth, noise_level)
        
        # 4. Set container and compression
        if file_type.lower() == 'tiff':
            ext = ".tif"
            # Optimization for 1-bit TIFF
            if bit_depth == 1:
                save_params = {"compression": "group4"} # Standard for B/W Fax/RIP
            else:
                save_params = {"compression": "packbits"}
        else: # BMP
            ext = ".bmp"
            save_params = {}
            
        # 5. Save to final output
        fd, final_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        
        result.save(final_path, **save_params)
        
        # Also create a PNG preview for the web
        # CRITICAL: Resize for web viewing. 1200DPI is too big for browser canvas (black screen issue)
        fd_p, preview_path = tempfile.mkstemp(suffix=".png")
        os.close(fd_p)
        
        # Create a copy for preview and resize it
        preview_img = result.copy()
        
        # Max dimension for preview (e.g. 2048px)
        MAX_PREVIEW_SIZE = 2048
        if preview_img.width > MAX_PREVIEW_SIZE or preview_img.height > MAX_PREVIEW_SIZE:
             preview_img.thumbnail((MAX_PREVIEW_SIZE, MAX_PREVIEW_SIZE), Image.Resampling.NEAREST)
        
        # Convert to RGB for consistency
        preview_img.convert("RGB").save(preview_path)
        
        return final_path, preview_path
        
    finally:
        # Cleanup intermediate
        if os.path.exists(gray_tif):
            os.remove(gray_tif)
