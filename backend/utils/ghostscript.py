import subprocess
import os
import tempfile

def rasterize_pdf(pdf_path: str, dpi: int = 300):
    """
    Uses Ghostscript to convert a PDF to a high-res grayscale TIFF (intermediate).
    Returns path to the intermediate file.
    """
    fd, output_path = tempfile.mkstemp(suffix=".tif")
    os.close(fd)
    
    # GS command to output grayscale TIFF
    # Using tiffgray for high-quality grayscale
    gs_cmd = [
        "gs",
        "-dNOPAUSE",
        "-dBATCH",
        "-sDEVICE=tiffgray",
        f"-r{dpi}",
        f"-sOutputFile={output_path}",
        pdf_path
    ]
    
    try:
        subprocess.run(gs_cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"Ghostscript failed: {e.stderr.decode()}")
    except FileNotFoundError:
        raise RuntimeError("Ghostscript (gs) NOT found in PATH. Please install it.")
