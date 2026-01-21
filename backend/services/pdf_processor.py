import os
import tempfile
from PIL import Image
from utils.ghostscript import rasterize_pdf
from utils.dithering import floyd_steinberg_dither

# Disable PIL's DecompressionBomb warning as we expect large images for RIP2
Image.MAX_IMAGE_PIXELS = None

def process_pdf_to_rip(pdf_path: str, output_format: str, dpi: int | str = 300, noise_level: float = 0.0, threads: int = 8, memory_mb: int = 2000):
    """
    Orchestrates the conversion from PDF to screened image.
    output_format: 'tiff1b', 'bmp2b', 'bmp4b', 'bmp8b'
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
        
        # 3. Apply dithering based on format
        if output_format == 'tiff1b':
            result = floyd_steinberg_dither(img, 1, noise_level)
            ext = ".tif"
            save_params = {"compression": "packbits"} # or tiff_ccitt if preferred for 1b
        elif output_format == 'bmp2b':
            result = floyd_steinberg_dither(img, 2, noise_level)
            ext = ".bmp"
            save_params = {}
        elif output_format == 'bmp4b':
            result = floyd_steinberg_dither(img, 4, noise_level)
            ext = ".bmp"
            save_params = {}
        elif output_format == 'bmp8b':
            result = floyd_steinberg_dither(img, 8, noise_level)
            ext = ".bmp"
            save_params = {}
        else:
            raise ValueError(f"Unsupported format: {output_format}")
            
        # 4. Save to final output
        fd, final_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        
        result.save(final_path, **save_params)
        
        # Also create a PNG preview for the web
        fd_p, preview_path = tempfile.mkstemp(suffix=".png")
        os.close(fd_p)
        
        # Convert to RGB for preview if needed, or just save as is
        result.convert("RGB").save(preview_path)
        
        return final_path, preview_path
        
    finally:
        # Cleanup intermediate
        if os.path.exists(gray_tif):
            os.remove(gray_tif)
