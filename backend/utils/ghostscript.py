import subprocess
import os
import tempfile

def rasterize_pdf(pdf_path: str, dpi: int | tuple[int, int] = 300):
    """
    Uses Ghostscript to convert a PDF to a high-res grayscale TIFF (intermediate).
    Returns path to the intermediate file.
    dpi: int for symmetric resolution (e.g. 300) or tuple (x_res, y_res) e.g. (1200, 600)
    """
    fd, output_path = tempfile.mkstemp(suffix=".tif")
    os.close(fd)
    
    # Handle DPI formatting for GS
    if isinstance(dpi, tuple) or isinstance(dpi, list):
        res_flag = f"-r{dpi[0]}x{dpi[1]}"
    else:
        res_flag = f"-r{dpi}"

    # GS command to output grayscale TIFF
    # Using tiffgray for high-quality grayscale
    gs_cmd = [
        "gs",
        "-dNOPAUSE",
        "-dBATCH",
        "-sDEVICE=tiffgray",
        res_flag,
        f"-sOutputFile={output_path}",
        pdf_path
    ]
    
    # Log command for debugging
    print(f"[Ghostscript] Executing: {' '.join(gs_cmd)}")
    
    try:
        subprocess.run(gs_cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"Ghostscript failed: {e.stderr.decode()}")
    except FileNotFoundError:
        raise RuntimeError("Ghostscript (gs) NOT found in PATH. Please install it.")
