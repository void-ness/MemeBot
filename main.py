from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
from fastapi.responses import FileResponse
import os
import tempfile
from meme_generator import MemeGeneratorManager  # Assuming this is in meme_generator.py

app = FastAPI()

class URLList(BaseModel):
    urls: List[str]

@app.post("/generate-meme")
async def generate_meme(url_list: URLList):
    if len(url_list.urls) != 4:
        raise HTTPException(status_code=400, detail="Exactly 4 URLs are required")
    
    # Create a temporary directory to store the output video
    with tempfile.TemporaryDirectory() as temp_dir:
        # output_path = os.path.join(temp_dir, "output_meme.mp4")
        output_path = "media/video/output_meme.mp4"
        
        # Initialize MemeGeneratorManager with the temporary output path
        meme_generator = MemeGeneratorManager(urls=url_list.urls, output_path=output_path)
        
        try:
            # Generate the meme
            meme_generator.generate_meme()
            
            # Return the video file as a response
            return FileResponse(output_path, media_type="video/mp4", filename="meme.mp4")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Meme generation failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)