# Claude Code Prompt for Z-Image-Turbo Deployment

Use this prompt when working with Claude Code in your IDE to get help with the deployment.

---

## Initial Setup Prompt

```
I'm deploying Z-Image-Turbo (6B image generation model) on RunPod serverless GPU with REST API. 

Project structure:
- handler.py: RunPod serverless handler
- Dockerfile.lightweight: Docker image (5GB, model downloads on first run)
- docker-build.yml: GitHub Actions workflow for automatic building
- client.py: Python API client
- requirements.txt: Dependencies

My goal: Deploy to RunPod without using local storage (using GitHub Actions).

Current step: [describe where you are]

Help me with: [what you need]
```

---

## Common Tasks & Prompts

### 1. Setting Up GitHub Repository

```
Help me set up a GitHub repository for this project:

Files to commit:
- handler.py
- Dockerfile.lightweight
- requirements.txt
- .github/workflows/docker-build.yml
- client.py
- .gitignore

Show me the exact git commands to:
1. Initialize the repo
2. Add files
3. Create first commit
4. Push to GitHub

Also, what should I put in .gitignore for this Python/Docker project?
```

### 2. Configuring GitHub Actions

```
I need to set up GitHub Actions secrets for Docker Hub:

1. Where exactly do I add DOCKERHUB_USERNAME and DOCKERHUB_TOKEN in GitHub?
2. How do I create a Docker Hub access token?
3. Should I use my Docker Hub password or an access token?
4. How do I verify the workflow is correctly configured?

Walk me through each step.
```

### 3. Testing Handler Locally

```
I want to test handler.py locally before deploying. 

My setup:
- GPU: [your GPU model or "no GPU"]
- Python version: [version]
- CUDA: [installed or not]

Help me:
1. Install dependencies correctly
2. Test the handler without RunPod
3. Mock the RunPod job structure for testing
4. Handle any errors that come up

Show me the exact commands and code.
```

### 4. Deploying to RunPod

```
I'm ready to deploy to RunPod. My Docker image is pushed to Docker Hub.

Guide me through:
1. Exact settings for RunPod endpoint configuration
2. What GPU should I choose for best cost/performance?
3. Container disk size needed
4. Worker scaling settings (min/max workers)
5. Timeout settings
6. How to get my endpoint ID and API key

Be specific about each setting.
```

### 5. Integrating with My Content Tool

```
I need to integrate this with my content creation tool.

My tech stack:
- Backend: [Django/Flask/FastAPI/Node.js/etc]
- Frontend: [React/Vue/Next.js/etc]
- Database: [PostgreSQL/MongoDB/etc]

Requirements:
- Users submit prompts through my UI
- Queue generation requests
- Show generation progress/status
- Store generated images
- Handle errors gracefully

Show me:
1. Backend integration code
2. Frontend code for calling the API
3. Database schema for storing results
4. Error handling patterns
5. How to implement a queue system
```

### 6. Debugging Issues

```
I'm getting this error: [paste error here]

Context:
- What I was doing: [describe]
- Code that failed: [paste code]
- Environment: [RunPod/Local/GitHub Actions]
- Full error trace: [paste if available]

Help me:
1. Understand what's wrong
2. Fix the issue
3. Prevent it in the future
```

### 7. Optimizing Performance

```
My deployment is working but I want to optimize:

Current metrics:
- Cold start time: [time]
- Generation time: [time]
- Cost per image: [cost]
- Issues: [any problems]

Help me:
1. Reduce cold start time
2. Speed up generation
3. Reduce costs
4. Improve reliability

What changes should I make to handler.py, Dockerfile, or RunPod settings?
```

### 8. Adding Features

```
I want to add these features to my deployment:

[Choose what you need:]
- ✅ Batch processing (multiple images at once)
- ✅ Image-to-image generation
- ✅ Upscaling/enhancement
- ✅ Style presets
- ✅ Negative prompts
- ✅ Image editing mode
- ✅ Custom aspect ratios
- ✅ Webhook notifications
- ✅ S3 storage integration
- ✅ Progress callbacks

For [specific feature], show me:
1. Modified handler.py code
2. Updated client.py code
3. API usage examples
4. Any additional dependencies
```

### 9. Production Deployment

```
I'm ready to move from testing to production.

Help me set up:
1. Environment separation (dev/staging/prod)
2. Monitoring and logging (track errors, performance)
3. Rate limiting and API keys
4. Database for job tracking
5. Retry logic for failed generations
6. Health checks and alerting
7. Cost tracking and budgets
8. Backup/fallback endpoints

Show me the production-ready code and infrastructure setup.
```

### 10. Scaling for High Traffic

```
My app is getting lots of traffic:
- Current: [X requests/day]
- Expected: [Y requests/day]
- Peak times: [when]

Help me scale:
1. Auto-scaling configuration for RunPod
2. Queue system (Redis/RabbitMQ/AWS SQS)
3. Caching strategy (avoid regenerating same prompts)
4. Load balancing across multiple endpoints
5. Cost optimization for high volume

Show me the architecture and code changes needed.
```

---

## Quick Reference Commands

### Git Commands
```bash
# Initialize and push
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main

# Check status
git status
git log --oneline

# Update after changes
git add .
git commit -m "Description of changes"
git push
```

### Docker Commands (if building locally)
```bash
# Build lightweight version
docker build -f Dockerfile.lightweight -t USERNAME/z-image-turbo:latest .

# Test locally (if you have GPU)
docker run --gpus all -p 8000:8000 USERNAME/z-image-turbo:latest

# Push to Docker Hub
docker login
docker push USERNAME/z-image-turbo:latest
```

### Python Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Test handler locally (requires GPU)
python test_handler.py

# Run local development server
python local_server.py

# Test client
python client.py
```

### API Testing with curl
```bash
# Test RunPod endpoint
curl -X POST https://api.runpod.ai/v2/ENDPOINT_ID/runsync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer API_KEY" \
  -d '{
    "input": {
      "prompt": "beautiful sunset",
      "seed": 42
    }
  }'
```

---

## Environment Variables Setup

Create `.env` file (DON'T commit this!):
```bash
RUNPOD_ENDPOINT_ID=your_endpoint_id
RUNPOD_API_KEY=your_api_key
DOCKERHUB_USERNAME=your_username
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()

endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
api_key = os.getenv('RUNPOD_API_KEY')
```

---

## Troubleshooting Checklist

When something goes wrong:

1. ✅ Check GitHub Actions build logs
2. ✅ Verify Docker image exists on Docker Hub
3. ✅ Check RunPod endpoint logs
4. ✅ Verify API credentials are correct
5. ✅ Test with simple prompt first
6. ✅ Check GPU availability on RunPod
7. ✅ Verify container disk size is sufficient (25GB+)
8. ✅ Check timeout settings
9. ✅ Review error messages in response
10. ✅ Test locally with test_handler.py

---

## Key Information to Have Ready

When asking Claude Code for help, provide:

```
Project: Z-Image-Turbo RunPod Deployment
Files: handler.py, Dockerfile.lightweight, client.py, docker-build.yml
Status: [dev/testing/production]
Environment: [local/GitHub Actions/RunPod]
Python Version: [X.X]
Docker Image: [username/z-image-turbo:latest]
RunPod Endpoint: [endpoint_id]
Current Issue: [describe problem]
What I've Tried: [steps taken]
Error Message: [paste full error]
```

---

## Next Steps Template

```
I've successfully [completed step].

Now I need to:
1. [Next task]
2. [Following task]
3. [Final goal]

Currently stuck on: [specific issue]

Show me the exact steps and code for [next task].
```

---

## Copy-Paste Ready Prompts

### For Starting Fresh:
```
I just downloaded the Z-Image-Turbo deployment files. I have:
- handler.py
- Dockerfile.lightweight  
- docker-build.yml
- client.py
- requirements.txt

I want to deploy this to RunPod using GitHub Actions (zero local storage).

My environment:
- OS: [Windows/Mac/Linux]
- Git installed: [yes/no]
- Docker Hub account: [yes/no]
- GitHub account: [yes/no]
- RunPod account: [yes/no]

Walk me through the complete setup process step by step, starting from creating the GitHub repository.
```

### For Integration Help:
```
My Z-Image-Turbo endpoint is live on RunPod:
- Endpoint ID: [YOUR_ENDPOINT_ID]
- API Key: [YOUR_API_KEY]
- Status: Working ✅

Now I need to integrate it with my [Django/Flask/Node.js] application.

My app structure:
[Describe your app]

Show me how to:
1. Add the client code to my project
2. Create an API endpoint that calls RunPod
3. Handle async image generation
4. Store results in database
5. Display images to users

Provide complete, production-ready code.
```

---

## Tips for Working with Claude Code

1. **Be specific**: Include exact error messages, file names, line numbers
2. **Share context**: Your OS, Python version, GPU specs (if testing locally)
3. **One task at a time**: Break complex problems into steps
4. **Share code**: Paste relevant code snippets, not just descriptions
5. **Mention what you've tried**: Helps avoid suggesting the same solutions

---

## Example Complete Workflow Prompt

```
Help me deploy Z-Image-Turbo end-to-end:

GOAL: Deploy to RunPod, integrate with my Flask app, store images in S3

CURRENT STATUS:
- ✅ Have all deployment files
- ❌ Haven't created GitHub repo yet
- ❌ No Docker Hub account yet
- ✅ Have RunPod account
- ✅ Have AWS S3 bucket

STEP-BY-STEP GUIDE NEEDED FOR:

1. GitHub Setup
   - Create repo
   - Add secrets for Docker Hub
   - Push code
   - Verify Actions build

2. Docker Hub Setup
   - Create account
   - Create access token
   - Verify image is pushed

3. RunPod Deployment
   - Configure endpoint
   - Choose GPU
   - Test deployment

4. Flask Integration
   - Install client
   - Create /generate endpoint
   - Handle async jobs
   - Upload to S3
   - Return S3 URL to user

5. Testing
   - Test each component
   - End-to-end test
   - Load testing

Provide complete code and commands for each step. I'll tell you when I'm ready for the next step.
```

---

Save this prompt template and use it whenever you need help with Claude Code! Good luck with your deployment! 🚀
