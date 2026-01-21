# Stochastic RIP Engine

A high-performance web-based Raster Image Processor (RIP) that converts vector PDFs into stochastically screened bitmap images using the **Floyd-Steinberg Error Diffusion** algorithm.

Built with **FastAPI** (Python) and **React** (Vite).

## 🚀 Features

*   **PDF Rasterization**: Uses **Ghostscript** for high-fidelity, high-resolution grayscale conversion.
*   **Stochastic Screening**: Implements Floyd-Steinberg dithering to convert grayscale tones into frequency-modulated (FM) halftones.
*   **Multi-Bit Depth Support**:
    *   **TIFF 1-bit**: Pure binary black/white.
    *   **BMP 2-bit**: 4-color palette.
    *   **BMP 4-bit**: 16-color palette.
    *   **BMP 8-bit**: 256-level screened grayscale.
*   **Advanced Controls**:
    *   **Asymmetric Resolution**: Support for non-square resolutions (e.g., `1200x600` DPI).
    *   **Noise Injection**: Configurable noise to break repetitive "worming" patterns inherent to error diffusion.
*   **Modern UI**: Dark-themed, responsive interface with drag-and-drop and live preview.

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Node.js 18+**
*   **Ghostscript**: Must be installed and available in the system `PATH`.
    *   Windows: Download from ghostscript.com and ensure the `bin` folder is in your Environment Variables.

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd RIP2
```

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment.
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies.
```bash
cd ../frontend
npm install
```

## ▶️ Usage

### Start the Backend
```bash
cd backend
python main.py
```
The API runs on `http://localhost:8000`.

### Start the Frontend
```bash
cd frontend
npm run dev
```
The interface runs on `http://localhost:5173`.

## 🧩 Architecture

*   **Frontend**: Sends the PDF and configuration (DPI, Format, Noise) to the API.
*   **Backend**:
    1.  Receives file.
    2.  Calls **Ghostscript** (subprocess) to generate a high-res Grayscale TIFF.
    3.  Loads TIFF into memory (PIL/NumPy).
    4.  Applies **Floyd-Steinberg** algorithm with optional noise injection map.
    5.  Packs bits according to the selected output format.
    6.  Returns a PNG preview url and a download link for the RAW file.

## 📄 License
MIT License.
