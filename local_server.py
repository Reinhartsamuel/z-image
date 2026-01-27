"""
FastAPI wrapper for local development and testing

This allows you to run the handler locally with a REST API
before deploying to RunPod.

Usage:
    pip install fastapi uvicorn
    python local_server.py
    
Then test with:
    curl -X POST http://localhost:8000/generate \
      -H "Content-Type: application/json" \
      -d '{"prompt": "beautiful sunset", "seed": 42}'
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional
import base64
import uvicorn

app = FastAPI(
    title="Z-Image-Turbo Local Server",
    description="Local development server for Z-Image-Turbo",
    version="1.0.0"
)


class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text description of the image to generate")
    height: int = Field(1024, description="Image height (must be multiple of 8)")
    width: int = Field(1024, description="Image width (must be multiple of 8)")
    num_inference_steps: int = Field(9, description="Number of denoising steps")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class GenerationResponse(BaseModel):
    image: str = Field(..., description="Base64-encoded PNG image")
    format: str = Field("base64", description="Image format")
    prompt: str
    seed: Optional[int]
    height: int
    width: int


@app.on_event("startup")
async def load_model():
    """Load the model on startup"""
    print("Loading Z-Image-Turbo model...")
    global pipe
    
    import torch
    from diffusers import ZImagePipeline
    
    pipe = ZImagePipeline.from_pretrained(
        "Tongyi-MAI/Z-Image-Turbo",
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=False,
    )
    pipe.to("cuda")
    
    try:
        pipe.transformer.set_attention_backend("flash")
        print("Flash Attention enabled")
    except Exception as e:
        print(f"Flash Attention not available: {e}")
    
    print("Model loaded successfully!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "model": "Z-Image-Turbo",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/generate", response_model=GenerationResponse)
async def generate_image(request: GenerationRequest):
    """Generate an image from a text prompt"""
    try:
        import torch
        from io import BytesIO
        
        # Validate dimensions
        if request.height % 8 != 0 or request.width % 8 != 0:
            raise HTTPException(
                status_code=400,
                detail="Height and width must be multiples of 8"
            )
        
        # Set up generator
        generator = None
        if request.seed is not None:
            generator = torch.Generator("cuda").manual_seed(request.seed)
        
        # Generate image
        print(f"Generating image: {request.prompt[:50]}...")
        image = pipe(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=0.0,
            generator=generator,
        ).images[0]
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return GenerationResponse(
            image=img_base64,
            format="base64",
            prompt=request.prompt,
            seed=request.seed,
            height=request.height,
            width=request.width
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/url")
async def generate_image_url(request: GenerationRequest):
    """Generate an image and return as downloadable PNG"""
    try:
        import torch
        from io import BytesIO
        
        # Validate dimensions
        if request.height % 8 != 0 or request.width % 8 != 0:
            raise HTTPException(
                status_code=400,
                detail="Height and width must be multiples of 8"
            )
        
        # Set up generator
        generator = None
        if request.seed is not None:
            generator = torch.Generator("cuda").manual_seed(request.seed)
        
        # Generate image
        image = pipe(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=0.0,
            generator=generator,
        ).images[0]
        
        # Convert to bytes
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        
        return Response(
            content=buffered.getvalue(),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=generated_{request.seed or 'random'}.png"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import torch
    
    # Check CUDA
    if not torch.cuda.is_available():
        print("⚠️  WARNING: CUDA not available!")
        print("   This server requires a CUDA-capable GPU.")
        import sys
        sys.exit(1)
    
    print("Starting local development server...")
    print("API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
