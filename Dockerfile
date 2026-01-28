FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy handler script
COPY handler.py /app/handler.py

# Pre-download the model to speed up cold starts
# This will cache the model in the Docker image (~14GB)
# NOTE: Commented out to avoid build timeouts - model will download on first cold start
# RUN python -c "from diffusers import ZImagePipeline; import torch; ZImagePipeline.from_pretrained('Tongyi-MAI/Z-Image-Turbo', torch_dtype=torch.bfloat16)"

# Set the entrypoint
CMD ["python", "-u", "handler.py"]
