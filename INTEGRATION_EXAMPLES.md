# Z-Image-Turbo Integration Examples

This file contains integration examples for various frameworks and languages.

## Python Integration Examples

### 1. Django Integration

```python
# views.py
from django.http import JsonResponse, HttpResponse
from django.views import View
from client import ZImageClient
import base64

class GenerateImageView(View):
    def __init__(self):
        super().__init__()
        self.client = ZImageClient(
            endpoint_id=settings.RUNPOD_ENDPOINT_ID,
            api_key=settings.RUNPOD_API_KEY
        )
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt')
            
            if not prompt:
                return JsonResponse({'error': 'Prompt required'}, status=400)
            
            # Generate image
            image = self.client.generate_sync(
                prompt=prompt,
                height=data.get('height', 1024),
                width=data.get('width', 1024),
                seed=data.get('seed')
            )
            
            # Return as base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return JsonResponse({
                'image': img_base64,
                'prompt': prompt
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# urls.py
from django.urls import path
from .views import GenerateImageView

urlpatterns = [
    path('api/generate/', GenerateImageView.as_view()),
]
```

### 2. Flask Integration

```python
# app.py
from flask import Flask, request, jsonify, send_file
from client import ZImageClient
import os
import base64
from io import BytesIO

app = Flask(__name__)

client = ZImageClient(
    endpoint_id=os.getenv('RUNPOD_ENDPOINT_ID'),
    api_key=os.getenv('RUNPOD_API_KEY')
)

@app.route('/api/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400
        
        # Generate image
        image = client.generate_sync(
            prompt=prompt,
            height=data.get('height', 1024),
            width=data.get('width', 1024),
            seed=data.get('seed')
        )
        
        # Return as base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'image': img_base64,
            'prompt': prompt
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/download', methods=['POST'])
def generate_and_download():
    try:
        data = request.get_json()
        image = client.generate_sync(prompt=data['prompt'])
        
        # Return as downloadable file
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)
        
        return send_file(
            buffered,
            mimetype='image/png',
            as_attachment=True,
            download_name='generated.png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. FastAPI Integration

```python
# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from client import ZImageClient
import os
from io import BytesIO
from typing import Optional
import uuid

app = FastAPI()

client = ZImageClient(
    endpoint_id=os.getenv('RUNPOD_ENDPOINT_ID'),
    api_key=os.getenv('RUNPOD_API_KEY')
)

# In-memory job storage (use Redis in production)
jobs = {}

class GenerateRequest(BaseModel):
    prompt: str
    height: int = 1024
    width: int = 1024
    seed: Optional[int] = None

class JobResponse(BaseModel):
    job_id: str
    status: str

@app.post("/generate/sync")
async def generate_sync(request: GenerateRequest):
    """Synchronous generation"""
    try:
        image = client.generate_sync(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            seed=request.seed
        )
        
        # Return as streaming response
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)
        
        return StreamingResponse(
            buffered,
            media_type="image/png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/async", response_model=JobResponse)
async def generate_async(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Asynchronous generation with job ID"""
    job_id = str(uuid.uuid4())
    
    # Store job
    jobs[job_id] = {"status": "pending", "image": None}
    
    # Process in background
    background_tasks.add_task(process_job, job_id, request)
    
    return JobResponse(job_id=job_id, status="pending")

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Check job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/job/{job_id}/image")
async def get_job_image(job_id: str):
    """Download job result"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    return StreamingResponse(
        job["image"],
        media_type="image/png"
    )

def process_job(job_id: str, request: GenerateRequest):
    """Background job processor"""
    try:
        image = client.generate_sync(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            seed=request.seed
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)
        
        jobs[job_id] = {
            "status": "completed",
            "image": buffered
        }
        
    except Exception as e:
        jobs[job_id] = {
            "status": "failed",
            "error": str(e)
        }
```

### 4. Celery Integration (Background Jobs)

```python
# tasks.py
from celery import Celery
from client import ZImageClient
import os

app = Celery('tasks', broker='redis://localhost:6379/0')

client = ZImageClient(
    endpoint_id=os.getenv('RUNPOD_ENDPOINT_ID'),
    api_key=os.getenv('RUNPOD_API_KEY')
)

@app.task
def generate_image_task(prompt, height=1024, width=1024, seed=None, user_id=None):
    """Background task for image generation"""
    try:
        image = client.generate_sync(
            prompt=prompt,
            height=height,
            width=width,
            seed=seed
        )
        
        # Save to S3, database, etc.
        filename = f"generated_{seed or 'random'}.png"
        image.save(f"/tmp/{filename}")
        
        # Upload to your storage
        # s3.upload_file(f"/tmp/{filename}", bucket, key)
        
        return {
            "status": "success",
            "filename": filename,
            "user_id": user_id
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

# Usage in your app
from tasks import generate_image_task

result = generate_image_task.delay(
    prompt="Beautiful sunset",
    seed=42,
    user_id=123
)

# Check result later
status = result.ready()
if status:
    output = result.get()
```

## JavaScript/TypeScript Integration

### 1. Next.js API Route

```typescript
// pages/api/generate.ts
import type { NextApiRequest, NextApiResponse } from 'next';

const RUNPOD_ENDPOINT = process.env.RUNPOD_ENDPOINT_ID;
const RUNPOD_API_KEY = process.env.RUNPOD_API_KEY;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { prompt, height = 1024, width = 1024, seed } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'Prompt required' });
  }

  try {
    const response = await fetch(
      `https://api.runpod.ai/v2/${RUNPOD_ENDPOINT}/runsync`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${RUNPOD_API_KEY}`,
        },
        body: JSON.stringify({
          input: { prompt, height, width, seed }
        })
      }
    );

    const result = await response.json();

    if (result.error) {
      throw new Error(result.error);
    }

    return res.status(200).json({
      image: result.output.image,
      prompt: result.output.prompt,
      seed: result.output.seed
    });

  } catch (error) {
    console.error('Generation error:', error);
    return res.status(500).json({
      error: error.message || 'Generation failed'
    });
  }
}
```

### 2. React Hook

```typescript
// hooks/useImageGeneration.ts
import { useState } from 'react';

interface GenerateOptions {
  prompt: string;
  height?: number;
  width?: number;
  seed?: number;
}

export function useImageGeneration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const generate = async (options: GenerateOptions) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
      });

      if (!response.ok) {
        throw new Error('Generation failed');
      }

      const data = await response.json();
      
      // Convert base64 to blob URL
      const blob = await fetch(`data:image/png;base64,${data.image}`)
        .then(r => r.blob());
      const url = URL.createObjectURL(blob);
      
      setImageUrl(url);
      return url;

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { generate, loading, error, imageUrl };
}

// Usage in component
function ImageGenerator() {
  const { generate, loading, error, imageUrl } = useImageGeneration();

  const handleGenerate = async () => {
    await generate({
      prompt: "Beautiful sunset over mountains",
      seed: 42
    });
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate'}
      </button>
      {error && <p>Error: {error}</p>}
      {imageUrl && <img src={imageUrl} alt="Generated" />}
    </div>
  );
}
```

### 3. Node.js Express

```javascript
// server.js
const express = require('express');
const fetch = require('node-fetch');

const app = express();
app.use(express.json());

const RUNPOD_ENDPOINT = process.env.RUNPOD_ENDPOINT_ID;
const RUNPOD_API_KEY = process.env.RUNPOD_API_KEY;

app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, height = 1024, width = 1024, seed } = req.body;

    const response = await fetch(
      `https://api.runpod.ai/v2/${RUNPOD_ENDPOINT}/runsync`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${RUNPOD_API_KEY}`,
        },
        body: JSON.stringify({
          input: { prompt, height, width, seed }
        })
      }
    );

    const result = await response.json();
    res.json(result.output);

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Environment Variables Template

Create a `.env` file:

```bash
# RunPod Configuration
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_API_KEY=your_api_key_here

# Optional: Default generation settings
DEFAULT_HEIGHT=1024
DEFAULT_WIDTH=1024
DEFAULT_STEPS=9
```

## Security Best Practices

1. **Never expose API keys** in frontend code
2. **Use environment variables** for all credentials
3. **Implement rate limiting** on your endpoints
4. **Add authentication** to your API routes
5. **Validate all inputs** before sending to RunPod
6. **Set up CORS** properly for web applications

## Production Considerations

1. **Caching**: Cache generated images by prompt+seed hash
2. **Queue System**: Use Redis/RabbitMQ for high-volume workloads
3. **Monitoring**: Track generation times, success rates
4. **Error Handling**: Implement retries for transient failures
5. **Cost Management**: Set spending alerts, monitor usage
