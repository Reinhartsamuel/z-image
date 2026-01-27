import os
import torch
import base64
from io import BytesIO
from diffusers import ZImagePipeline
import runpod

# Global model loading (happens once per worker)
print("Loading Z-Image-Turbo model...")
pipe = ZImagePipeline.from_pretrained(
    "Tongyi-MAI/Z-Image-Turbo",
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=False,
)
pipe.to("cuda")

# Optional: Configure attention backend
# Use eager attention for maximum compatibility with PyTorch versions
try:
    pipe.transformer.set_attention_backend("eager")
    print("Eager attention backend enabled")
except Exception as e:
    print(f"Could not set attention backend: {e}")
    # Continue anyway, model will use default attention

# Optional: Compile the model for faster inference (first run will be slower)
# Uncomment the line below if you want to enable compilation
# pipe.transformer.compile()

print("Model loaded successfully!")

def generate_image(job):
    """
    Handler function for RunPod serverless
    
    Expected input:
    {
        "prompt": "your prompt here",
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 9,
        "seed": 42
    }
    """
    try:
        job_input = job["input"]
        
        # Extract parameters with defaults
        prompt = job_input.get("prompt", "")
        height = job_input.get("height", 1024)
        width = job_input.get("width", 1024)
        num_inference_steps = job_input.get("num_inference_steps", 9)
        seed = job_input.get("seed", None)
        
        if not prompt:
            return {"error": "No prompt provided"}
        
        # Validate dimensions (must be multiples of 8)
        if height % 8 != 0 or width % 8 != 0:
            return {"error": "Height and width must be multiples of 8"}
        
        # Set up generator
        generator = None
        if seed is not None:
            generator = torch.Generator("cuda").manual_seed(seed)
        
        # Generate image
        print(f"Generating image for prompt: {prompt[:50]}...")
        image = pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            guidance_scale=0.0,  # Turbo models use guidance_scale=0
            generator=generator,
        ).images[0]
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image": img_base64,
            "format": "base64",
            "prompt": prompt,
            "seed": seed,
            "height": height,
            "width": width
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Start the serverless handler
runpod.serverless.start({"handler": generate_image})
