#!/bin/bash

# Build the Docker image
echo "Building toploc Docker image..."
docker build -t toploc .

# Run the container
echo "Starting toploc container..."
docker run -d \
  --name toploc-app \
  -p 6500:6500 \
  -v $(pwd)/trained_models:/app/trained_models \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/proofs:/app/proofs \
  toploc

echo "Toploc is running on http://localhost:6500"
echo "To stop the container: docker stop toploc-app"
echo "To remove the container: docker rm toploc-app" 