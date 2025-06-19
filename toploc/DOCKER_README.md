# Toploc Docker Setup

This directory contains Docker configuration for running the Toploc Flask application.

## Quick Start

### Option 1: Using Docker Compose (Recommended)
```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Option 2: Using the build script
```bash
# Make the script executable (if not already)
chmod +x build.sh

# Build and run
./build.sh
```

### Option 3: Manual Docker commands
```bash
# Build the image
docker build -t toploc .

# Run the container
docker run -d \
  --name toploc-app \
  -p 6500:6500 \
  -v $(pwd)/trained_models:/app/trained_models \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/proofs:/app/proofs \
  toploc
```

## Accessing the Application

The Flask application will be available at: http://localhost:6500

## API Endpoints

- `POST /run` - Main endpoint for running prediction or verification tasks

### Example Usage

```bash
# Run a prediction task
curl -X POST http://localhost:6500/run \
  -F "dataset_url=https://huggingface.co/datasets/your-dataset/resolve/main/data.csv" \
  -F "model_url=https://huggingface.co/your-model/resolve/main/model.pt" \
  -F "task=predict"

# Run a verification task
curl -X POST http://localhost:6500/run \
  -F "dataset_url=https://huggingface.co/datasets/your-dataset/resolve/main/data.csv" \
  -F "model_url=https://huggingface.co/your-model/resolve/main/model.pt" \
  -F "task=verify" \
  -F "proof=your_proof_data"
```

## Volumes

The following directories are mounted as volumes:
- `./trained_models` - For storing trained models
- `./models` - For storing model definitions
- `./proofs` - For storing generated proofs

## Dependencies

The Docker image includes only the necessary dependencies:
- `torch==2.0.1` - PyTorch for ML operations
- `numpy` - Numerical computing
- `pandas>=2.3.0` - Data manipulation
- `flask>=3.1.1` - Web framework
- `huggingface-hub>=0.33.0` - HuggingFace integration
- `scikit-learn` - Machine learning utilities
- `pymerkle>=6.1.0` - Merkle tree operations

## Troubleshooting

### Container won't start
Check the logs:
```bash
docker logs toploc-app
```

### Port already in use
If port 6500 is already in use, you can change it in the docker-compose.yml or docker run command:
```bash
docker run -p 6501:6500 toploc
```

### Permission issues with volumes
Make sure the directories exist and have proper permissions:
```bash
mkdir -p trained_models models proofs
chmod 755 trained_models models proofs
``` 