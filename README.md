# Z-Image-Turbo RunPod Serverless Deployment

Complete setup for deploying Z-Image-Turbo on RunPod serverless GPUs with REST API access.

## 📁 Project Structure

```
.
├── handler.py          # RunPod serverless handler
├── Dockerfile          # Docker image for deployment
├── requirements.txt    # Python dependencies
├── client.py           # Python client for API calls
└── README.md          # This file
```

## 🚀 Quick Start

### Step 1: Build and Push Docker Image

```bash
# 1. Login to Docker Hub
docker login

# 2. Build the image (this will take ~15-20 minutes)
docker build -t YOUR_DOCKERHUB_USERNAME/z-image-turbo:latest .

# 3. Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/z-image-turbo:latest
```

**Note:** The Docker image will be ~20GB because it includes the pre-downloaded model weights.

### Step 2: Deploy on RunPod

1. Go to [RunPod Serverless](https://www.runpod.io/console/serverless)
2. Click **"+ New Endpoint"**
3. Configure the endpoint:

#### Basic Settings
- **Endpoint Name**: `z-image-turbo`
- **Container Image**: `YOUR_DOCKERHUB_USERNAME/z-image-turbo:latest`
- **Container Disk**: `25 GB` (for model + temp files)

#### GPU Configuration
Choose one of these GPU types:
- **RTX 4090** - Recommended, ~$0.34/hour, ~2-3s per image
- **RTX A6000** - Good alternative, ~$0.79/hour, ~2s per image  
- **RTX A40** - Budget option, ~$0.69/hour, ~3-4s per image
- **A100** - Overkill but fastest, ~$1.89/hour, <1s per image

#### Scaling Configuration
- **Min Workers**: `0` (scale to zero when idle)
- **Max Workers**: `3-10` (depending on your traffic)
- **Idle Timeout**: `5 seconds`
- **Execution Timeout**: `60 seconds`

#### Advanced Settings (Optional)
- **Flash Boot**: Enabled (faster cold starts)
- **Environment Variables**: None needed

4. Click **"Deploy"**

### Step 3: Get Your Credentials

After deployment:
1. Click on your endpoint
2. Copy your **Endpoint ID** (looks like: `abc123def456`)
3. Go to **Settings** → **API Keys**
4. Copy or create a new **API Key**

### Step 4: Test the API

Update `client.py` with your credentials:

```python
client = ZImageClient(
    endpoint_id="YOUR_ENDPOINT_ID",
    api_key="YOUR_API_KEY"
)

# Generate an image
image = client.generate_sync(
    prompt="Young Chinese woman in red Hanfu, intricate embroidery",
    seed=42
)
image.save("output.png")
```

Run the client:

```bash
python client.py
```

## 💡 Usage Examples

### Synchronous Generation (Wait for Result)

```python
from client import ZImageClient

client = ZImageClient(
    endpoint_id="YOUR_ENDPOINT_ID",
    api_key="YOUR_API_KEY"
)

# Generate and get result immediately
image = client.generate_sync(
    prompt="Beautiful sunset over mountains",
    height=1024,
    width=1024,
    seed=42
)
image.save("output.png")
```

### Asynchronous Generation (Submit and Check Later)

```python
# Submit job
job_id = client.generate_async(
    prompt="Futuristic cityscape at night",
    seed=123
)

# Do other work...

# Get result when ready
image = client.get_result(job_id, wait=True, max_wait=120)
image.save("output.png")
```

### Batch Processing

```python
prompts = [
    "A serene Japanese garden",
    "Ancient temple in mountains",
    "Cyberpunk city street"
]

# Submit all jobs
job_ids = [client.generate_async(p) for p in prompts]

# Collect results
images = [client.get_result(job_id) for job_id in job_ids]

# Save
for i, img in enumerate(images):
    img.save(f"output_{i}.png")
```

### REST API Direct Call (curl)

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": {
      "prompt": "Beautiful sunset over mountains",
      "height": 1024,
      "width": 1024,
      "num_inference_steps": 9,
      "seed": 42
    }
  }'
```

### JavaScript/TypeScript Example

```javascript
async function generateImage(prompt) {
  const response = await fetch(
    'https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'
      },
      body: JSON.stringify({
        input: {
          prompt: prompt,
          height: 1024,
          width: 1024,
          num_inference_steps: 9,
          seed: 42
        }
      })
    }
  );
  
  const result = await response.json();
  const imageBase64 = result.output.image;
  
  // Convert base64 to blob for download
  const imageBlob = await fetch(`data:image/png;base64,${imageBase64}`).then(r => r.blob());
  return imageBlob;
}
```

## 📊 API Reference

### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | **required** | Text description of the image |
| `height` | integer | 1024 | Image height (must be multiple of 8) |
| `width` | integer | 1024 | Image width (must be multiple of 8) |
| `num_inference_steps` | integer | 9 | Number of denoising steps (8-16 recommended) |
| `seed` | integer | null | Random seed for reproducibility |

### Response Format

```json
{
  "output": {
    "image": "base64_encoded_png_string",
    "format": "base64",
    "prompt": "your prompt",
    "seed": 42,
    "height": 1024,
    "width": 1024
  }
}
```

### Error Response

```json
{
  "output": {
    "error": "Error message",
    "traceback": "Full error traceback"
  }
}
```

## 🔧 Configuration Options

### Optimize for Speed

In `handler.py`, uncomment this line:

```python
pipe.transformer.compile()
```

This gives 20-30% speedup but increases cold start time by ~30 seconds.

### Enable Flash Attention

Flash Attention is already enabled by default in `handler.py`:

```python
pipe.transformer.set_attention_backend("flash")
```

### Adjust Image Quality

In `client.py`, modify `num_inference_steps`:

```python
# Faster but lower quality
image = client.generate_sync(prompt="...", num_inference_steps=6)

# Slower but higher quality
image = client.generate_sync(prompt="...", num_inference_steps=12)
```

## 💰 Cost Estimation

### GPU Pricing (per hour)
- RTX 4090: ~$0.34
- RTX A6000: ~$0.79
- RTX A40: ~$0.69

### Cost per Image
Assuming RTX 4090 at $0.34/hour and 2 seconds per image:
- **Cost per image**: ~$0.0002 (2 cents per 100 images)
- **1000 images**: ~$0.20
- **10,000 images**: ~$2.00

### Scale to Zero Savings
With workers scaling to zero when idle, you only pay for actual generation time!

## 🐛 Troubleshooting

### "Out of Memory" Error
- Reduce resolution: Try 768x768 or 512x512
- Use a GPU with more VRAM (A40, A6000, A100)

### Cold Starts are Slow
- The first request after scaling to zero takes 15-30 seconds (model loading)
- Keep 1 worker alive during peak hours by setting Min Workers = 1
- Enable Flash Boot in RunPod settings

### Generation Quality is Poor
- Increase `num_inference_steps` to 12-16
- Ensure `guidance_scale=0.0` (Turbo models don't use CFG)
- Try different seeds to find good ones

### Timeout Errors
- Increase `timeout` parameter in client
- Check RunPod execution timeout setting (default 60s)

### Image is Corrupted/Blank
- Check that height/width are multiples of 8
- Verify the base64 decoding is correct
- Check RunPod logs for errors

## 📈 Performance Benchmarks

| GPU | VRAM | Cold Start | Generation Time | Cost/Image |
|-----|------|------------|-----------------|------------|
| RTX 4090 | 24GB | 20s | 2-3s | $0.0002 |
| RTX A6000 | 48GB | 20s | 2s | $0.0004 |
| RTX A40 | 48GB | 25s | 3-4s | $0.0004 |
| A100 | 80GB | 15s | <1s | $0.0011 |

## 🔒 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for credentials
3. **Implement rate limiting** in your application
4. **Monitor usage** via RunPod dashboard
5. **Set spending limits** in RunPod billing settings

## 📚 Additional Resources

- [Z-Image-Turbo Model Card](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo)
- [RunPod Documentation](https://docs.runpod.io/serverless/overview)
- [Diffusers Documentation](https://huggingface.co/docs/diffusers)

## 🆘 Support

- **RunPod Support**: support@runpod.io
- **Z-Image Issues**: https://github.com/Tongyi-MAI/Z-Image/issues
- **Diffusers Issues**: https://github.com/huggingface/diffusers/issues

## 📝 License

This deployment setup is provided as-is. Check the respective licenses for:
- Z-Image-Turbo: Apache 2.0
- RunPod: Check their terms of service
- Your usage: Comply with all applicable licenses
