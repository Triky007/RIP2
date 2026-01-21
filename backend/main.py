from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import tempfile
from services.pdf_processor import process_pdf_to_rip

app = FastAPI(title="RIP Application API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store results temporarily (In a real app, use a proper cleanup strategy)
PROCESSED_DATA = {}

@app.post("/process")
async def process_pdf(
    file: UploadFile = File(...),
    format: str = Form(...),
    dpi: str = Form("300"), # Accepts string now (e.g. "1200x600")
    noise: float = Form(0.0)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    # Save uploaded file
    fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    try:
        with open(temp_pdf, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process
        try:
            final_path, preview_path = process_pdf_to_rip(temp_pdf, format, dpi, noise)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
        file_id = os.path.basename(final_path)
        PROCESSED_DATA[file_id] = {
            "final": final_path,
            "preview": preview_path,
            "filename": f"processed_{os.path.basename(file.filename).split('.')[0]}{os.path.splitext(final_path)[1]}"
        }
        
        return {
            "id": file_id,
            "preview_url": f"/preview/{file_id}",
            "filename": PROCESSED_DATA[file_id]["filename"]
        }
        
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)

@app.get("/preview/{file_id}")
async def get_preview(file_id: str):
    if file_id not in PROCESSED_DATA:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(PROCESSED_DATA[file_id]["preview"], media_type="image/png")

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    if file_id not in PROCESSED_DATA:
        raise HTTPException(status_code=404, detail="File not found")
    
    data = PROCESSED_DATA[file_id]
    return FileResponse(
        data["final"], 
        filename=data["filename"],
        media_type="application/octet-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
