# Technical Documentation: Stochastic RIP

## Overview
This document details the technical implementation of the Stochastic RIP application, focusing on the image processing pipeline, the error diffusion algorithm, and the integration choices.

## 1. System Architecture

The application is split into two distinct services:
- **Core Processing Engine (Backend)**: Python-based service optimized for numerical array processing (`numpy`) and system I/O (`subprocess` for Ghostscript).
- **User Interface (Frontend)**: React application handling user inputs, file uploads, and preview visualization.

### Data Flow
1.  **User Request**: Upload PDF + Format (e.g., BMP 4-bit) + DPI (e.g., "1200x600") + Noise %.
2.  **Rasterization**: Backend invokes Ghostscript to interpret the PDF vectors.
3.  **Processing**: The grayscale raster is dithered in Python.
4.  **Formatting**: The dithered array is converted to the specific file format structure.
5.  **Response**: JSON pointing to temporary file resources.

## 2. Rasterization (Ghostscript)

We offload the initial rasterization to **Ghostscript** rather than using Python PDF libraries (like `pdf2image` or `pypdfiu`) because:
- **CMYK/Grayscale Accuracy**: Ghostscript is the industry standard for Printing/RIP tasks.
- **Resolution Control**: It supports arbitrary and asymmetric resolutions (e.g., `-r1200x600`) natively.
- **Performance**: It handles complex heavy vector PDFs efficiently.

**Command used:**
```bash
gs -dNOPAUSE -dBATCH -sDEVICE=tiffgray -r<DPI> -sOutputFile=<temp.tif> <input.pdf>
```

## 3. The Floyd-Steinberg Algorithm

The core characteristic of this RIP is **Stochastic Screening** (Frequency Modulated Halftoning), achieved via Error Diffusion.

### Standard Algorithm
For each pixel `P[x, y]`:
1.  **Quantize**: Find the nearest available color in the palette (e.g., Black or White for 1-bit).
2.  **Calculate Error**: `Error = Original_Value - Quantized_Value`
3.  **Diffuse**: Distribute portions of `Error` to neighbors:
    - `Right (+1, 0)`: 7/16
    - `Bottom-Left (-1, +1)`: 3/16
    - `Bottom (0, +1)`: 5/16
    - `Bottom-Right (+1, +1)`: 1/16

### Noise Injection (Pattern Breaking)
A common artifact of Floyd-Steinberg in uniform gray areas is "worming" (snake-like patterns). To mitigate this, we implemented a **Noise Injection** step:

```python
# Before quantizing
noise = (random() - 0.5) * intensity
pixel_value = pixel_value + noise
```
By perturbing the pixel value slightly before calculating the error, the diffusion paths are randomized, breaking the regular "worm" structures and producing a more film-grain-like texture.

## 4. Multi-Bit Depth Support

The application supports various outputs by adjusting the **Quantization Palette**:

| Format | Bit Depth | Colors | Quantization Levels |
| :--- | :--- | :--- | :--- |
| **TIFF 1-bit** | 1 | 2 (B/W) | `[0, 255]` |
| **BMP 2-bit** | 2 | 4 | `[0, 85, 170, 255]` |
| **BMP 4-bit** | 4 | 16 | `[0, 17, ..., 255]` (Linear steps) |
| **BMP 8-bit** | 8 | 256 | `[0, 1, ..., 255]` |

### Output Encoding
- **TIFF**: Saved using `packbits` compression (standard for simple run-length encoding).
- **BMP**: Saved as indexed color (Palette) for 2/4/8 bits.

## 5. Asymmetric Resolution
Industrial printheads often have different resolutions in the web direction vs. cross-web direction (e.g., 600dpi usually, but 1200dpi if the web moves slower).
We support strings like `"1200x600"`.
- **Parsing**: Split by `x`.
- **Ghostscript**: Passed as `-r1200x600`.
- **NumPy**: The array naturally adapts to the resulting aspect ratio (pixels are just data points).
- **Preview**: The web preview might look "stretched" if displayed 1:1, but the data is pixel-perfect for the device.
