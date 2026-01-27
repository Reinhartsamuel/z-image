import requests
import json
import base64
import time
from PIL import Image
from io import BytesIO
from typing import Optional, Dict, Any


class ZImageClient:
    """
    Client for interacting with Z-Image-Turbo RunPod serverless endpoint
    """
    
    def __init__(self, endpoint_id: str, api_key: str):
        """
        Initialize the client
        
        Args:
            endpoint_id: Your RunPod endpoint ID
            api_key: Your RunPod API key
        """
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def generate_sync(
        self,
        prompt: str,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 9,
        seed: Optional[int] = None,
        timeout: int = 120
    ) -> Image.Image:
        """
        Generate an image synchronously (wait for completion)
        
        Args:
            prompt: Text description of the image to generate
            height: Image height (must be multiple of 8)
            width: Image width (must be multiple of 8)
            num_inference_steps: Number of denoising steps (default: 9)
            seed: Random seed for reproducibility
            timeout: Maximum time to wait in seconds
            
        Returns:
            PIL Image object
        """
        url = f"{self.base_url}/runsync"
        
        payload = {
            "input": {
                "prompt": prompt,
                "height": height,
                "width": width,
                "num_inference_steps": num_inference_steps,
                "seed": seed
            }
        }
        
        print(f"Sending request to {url}")
        response = requests.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Check for errors in response
        if "error" in result:
            raise Exception(f"Generation failed: {result['error']}")
        
        # Decode base64 image
        output = result.get("output", {})
        if "error" in output:
            raise Exception(f"Generation failed: {output['error']}")
        
        img_base64 = output.get("image")
        if not img_base64:
            raise Exception(f"No image in response: {result}")
        
        img_data = base64.b64decode(img_base64)
        image = Image.open(BytesIO(img_data))
        
        return image
    
    def generate_async(
        self,
        prompt: str,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 9,
        seed: Optional[int] = None
    ) -> str:
        """
        Generate an image asynchronously (returns job ID immediately)
        
        Args:
            prompt: Text description of the image to generate
            height: Image height (must be multiple of 8)
            width: Image width (must be multiple of 8)
            num_inference_steps: Number of denoising steps (default: 9)
            seed: Random seed for reproducibility
            
        Returns:
            Job ID string
        """
        url = f"{self.base_url}/run"
        
        payload = {
            "input": {
                "prompt": prompt,
                "height": height,
                "width": width,
                "num_inference_steps": num_inference_steps,
                "seed": seed
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        return result.get("id")
    
    def check_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of an async job
        
        Args:
            job_id: Job ID returned from generate_async
            
        Returns:
            Status dictionary
        """
        url = f"{self.base_url}/status/{job_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Status check failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    def get_result(self, job_id: str, wait: bool = True, max_wait: int = 120) -> Optional[Image.Image]:
        """
        Get the result of an async job
        
        Args:
            job_id: Job ID returned from generate_async
            wait: Whether to wait for completion
            max_wait: Maximum time to wait in seconds
            
        Returns:
            PIL Image object or None if not ready
        """
        start_time = time.time()
        
        while True:
            status = self.check_status(job_id)
            
            job_status = status.get("status")
            
            if job_status == "COMPLETED":
                output = status.get("output", {})
                
                if "error" in output:
                    raise Exception(f"Generation failed: {output['error']}")
                
                img_base64 = output.get("image")
                img_data = base64.b64decode(img_base64)
                image = Image.open(BytesIO(img_data))
                
                return image
            
            elif job_status == "FAILED":
                error = status.get("error", "Unknown error")
                raise Exception(f"Job failed: {error}")
            
            elif job_status in ["IN_QUEUE", "IN_PROGRESS"]:
                if not wait:
                    return None
                
                elapsed = time.time() - start_time
                if elapsed > max_wait:
                    raise TimeoutError(f"Job did not complete within {max_wait} seconds")
                
                time.sleep(1)
            
            else:
                raise Exception(f"Unknown job status: {job_status}")
    
    def health_check(self) -> bool:
        """
        Check if the endpoint is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        url = f"{self.base_url}/health"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code == 200
        except:
            return False


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ZImageClient(
        endpoint_id="YOUR_ENDPOINT_ID",
        api_key="YOUR_API_KEY"
    )
    
    # Example 1: Synchronous generation (wait for result)
    print("Generating image synchronously...")
    image = client.generate_sync(
        prompt="Young Chinese woman in red Hanfu, intricate embroidery. Impeccable makeup, red floral forehead pattern.",
        height=1024,
        width=1024,
        seed=42
    )
    image.save("output_sync.png")
    print("Saved to output_sync.png")
    
    # Example 2: Asynchronous generation (submit and check later)
    print("\nGenerating image asynchronously...")
    job_id = client.generate_async(
        prompt="Beautiful sunset over mountains, photorealistic",
        seed=123
    )
    print(f"Job submitted: {job_id}")
    
    # Wait for result
    image = client.get_result(job_id, wait=True)
    image.save("output_async.png")
    print("Saved to output_async.png")
    
    # Example 3: Batch processing
    print("\nBatch processing multiple prompts...")
    prompts = [
        "A serene Japanese garden with cherry blossoms",
        "Futuristic cityscape at night with neon lights",
        "Ancient temple in misty mountains"
    ]
    
    # Submit all jobs
    job_ids = []
    for prompt in prompts:
        job_id = client.generate_async(prompt)
        job_ids.append(job_id)
        print(f"Submitted: {prompt[:50]}... -> {job_id}")
    
    # Collect results
    for i, job_id in enumerate(job_ids):
        image = client.get_result(job_id)
        image.save(f"batch_output_{i}.png")
        print(f"Saved batch_output_{i}.png")
