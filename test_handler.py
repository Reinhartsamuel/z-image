"""
Local test script for the handler.py

This simulates the RunPod environment for testing without deploying.
"""

import json
import base64
from PIL import Image
from io import BytesIO


def simulate_runpod_job(prompt, height=1024, width=1024, seed=None):
    """
    Simulate a RunPod job locally
    """
    # This would normally come from RunPod
    job = {
        "id": "test-job-123",
        "input": {
            "prompt": prompt,
            "height": height,
            "width": width,
            "num_inference_steps": 9,
            "seed": seed
        }
    }
    
    # Import handler (make sure handler.py is in the same directory)
    try:
        from handler import generate_image
    except ImportError:
        print("Error: handler.py not found. Make sure you're in the correct directory.")
        return None
    
    print(f"Testing with prompt: {prompt[:80]}...")
    result = generate_image(job)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        if "traceback" in result:
            print(f"Traceback:\n{result['traceback']}")
        return None
    
    # Decode and save the image
    img_base64 = result["image"]
    img_data = base64.b64decode(img_base64)
    image = Image.open(BytesIO(img_data))
    
    output_path = f"test_output_{seed or 'random'}.png"
    image.save(output_path)
    
    print(f"✅ Success! Image saved to {output_path}")
    print(f"   Dimensions: {result['width']}x{result['height']}")
    print(f"   Seed: {result['seed']}")
    
    return image


def run_tests():
    """
    Run a series of tests
    """
    print("="*80)
    print("Z-Image-Turbo Handler Tests")
    print("="*80)
    
    tests = [
        {
            "name": "Basic test",
            "prompt": "Young Chinese woman in red Hanfu, intricate embroidery",
            "seed": 42
        },
        {
            "name": "Different resolution",
            "prompt": "Beautiful sunset over mountains, photorealistic",
            "height": 768,
            "width": 768,
            "seed": 123
        },
        {
            "name": "English text rendering",
            "prompt": "A neon sign that says 'HELLO WORLD' in bright blue letters",
            "seed": 456
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(tests)}: {test['name']}")
        print(f"{'='*80}")
        
        result = simulate_runpod_job(
            prompt=test["prompt"],
            height=test.get("height", 1024),
            width=test.get("width", 1024),
            seed=test.get("seed")
        )
        
        if result is None:
            print(f"❌ Test {i} failed!")
            return False
    
    print(f"\n{'='*80}")
    print("✅ All tests passed!")
    print(f"{'='*80}")
    return True


if __name__ == "__main__":
    import sys
    
    # Check if CUDA is available
    try:
        import torch
        if not torch.cuda.is_available():
            print("⚠️  WARNING: CUDA not available. This will be very slow or fail!")
            print("   Make sure you have a CUDA-capable GPU and PyTorch with CUDA support.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
    except ImportError:
        print("❌ PyTorch not installed. Please install requirements first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Run tests
    success = run_tests()
    sys.exit(0 if success else 1)
