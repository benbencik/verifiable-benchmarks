# Verifiable Benchmarks

**Verifiable Benchmarks** is an open-source framework for trustless verification of machine learning inference, inspired by the [TOPLOC](https://arxiv.org/pdf/2501.16007) approach. This project addresses the critical challenge of establishing trust in third-party ML inference providers, ensuring that users can independently verify the integrity and faithfulness of off-chain model execution.

## 🎯 Vision: Democratizing Trust in AI

### The Problem: Trust Crisis in AI Services

As AI services become increasingly commoditized and outsourced, users face a fundamental trust problem:

- **Model Integrity**: How do you know the provider is running the exact model they claim?
- **Inference Fidelity**: How do you verify they're not cutting corners (reduced precision, smaller models, etc.)?
- **Result Authenticity**: How do you prove the results came from legitimate computation?
- **Cost Transparency**: How do you ensure you're paying for what you actually receive?

Traditional solutions rely on centralized trust authorities or expensive on-chain computation, both of which have significant limitations.

### Our Solution: Decentralized Verifiable Inference

We're building a **decentralized verification network** that provides cryptographic guarantees for ML inference without requiring trust in any single entity. Our approach combines:

1. **TOPLOC Protocol**: Locality-sensitive hashing of neural network activations that creates compact, verifiable proofs
2. **EigenLayer AVS**: Decentralized network of validators that independently verify proofs and reach consensus
3. **Economic Security**: Stake-based incentives that align validator behavior with honest verification

## 🔗 Why EigenLayer AVS?

### The Perfect Match for Verifiable ML

EigenLayer's Actively Validated Services (AVS) framework is uniquely suited for verifiable ML inference because:

#### **1. Decentralized Consensus Without Centralization**
- **Traditional Problem**: Centralized verification services become single points of failure and potential corruption
- **EigenLayer Solution**: Distributed network of validators with economic incentives to maintain integrity
- **Our Implementation**: Multiple operators independently verify the same inference task and reach consensus

#### **2. Economic Security Through Stake**
- **Traditional Problem**: Reputation-based systems are vulnerable to Sybil attacks and collusion
- **EigenLayer Solution**: Validators stake ETH, creating real economic consequences for dishonest behavior
- **Our Implementation**: Operators risk losing their stake if they verify incorrect results

#### **3. Scalable Off-Chain Computation**
- **Traditional Problem**: On-chain ML verification is prohibitively expensive and slow
- **EigenLayer Solution**: Off-chain computation with on-chain consensus and settlement
- **Our Implementation**: TOPLOC proofs are generated off-chain, verified by the AVS network, and results are settled on-chain

#### **4. Modular Security Architecture**
- **Traditional Problem**: Building verification infrastructure from scratch requires massive capital and coordination
- **EigenLayer Solution**: Leverages existing Ethereum security and validator infrastructure
- **Our Implementation**: Inherits Ethereum's security while adding specialized ML verification capabilities

### How It Works in Practice

1. **Task Submission**: User submits ML inference request with model and dataset URLs
2. **Proof Generation**: TOPLOC service generates compact cryptographic proof of inference execution
3. **AVS Verification**: Multiple EigenLayer operators independently:
   - Download the same model and dataset
   - Run the same inference
   - Generate their own TOPLOC proof
   - Compare with the submitted proof
4. **Consensus**: Operators reach consensus on whether the submitted proof is valid
5. **Settlement**: Results are recorded on-chain with economic guarantees

### Economic Model

- **Validators**: Earn fees for honest verification, risk slashing for dishonest behavior
- **Users**: Pay small fees for verification, receive cryptographic guarantees
- **Providers**: Can prove their service integrity, potentially commanding premium prices

## 🏗️ System Architecture

This project consists of three main components working together:

### 1. **EigenLayer AVS (Actively Validated Service)**
- **Location**: `verifiable-benchmarks-avs/`
- **Purpose**: Decentralized verification network using EigenLayer's AVS framework
- **Technology**: Go + Hourglass framework
- **Function**: Receives ML inference tasks, validates proofs, and reaches consensus

### 2. **TOPLOC Proof Generation Service**
- **Location**: `toploc/`
- **Purpose**: Generates cryptographic proofs of ML model inference
- **Technology**: Python + Flask API
- **Function**: Creates locality-sensitive hashing proofs of neural network activations

### 3. **Web Interface**
- **Location**: `ml-verification-interface/`
- **Purpose**: User-friendly interface for proof generation and verification
- **Technology**: Next.js + TypeScript + Tailwind CSS
- **Function**: Frontend for interacting with the verification system

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [Foundry](https://book.getfoundry.sh/getting-started/installation)
- [Go (v1.23.6)](https://go.dev/doc/install)
- [Node.js (v18+)](https://nodejs.org/)
- [Python (v3.8+)](https://www.python.org/)

### 1. Setup Environment Variables

```bash
cd verifiable-benchmarks-avs
cp .env.example .env
```

Edit `.env` and set your Ethereum fork URLs:
```bash
L1_FORK_URL=your_ethereum_rpc_url_here
L2_FORK_URL=your_ethereum_rpc_url_here
```

### 2. Start the TOPLOC Proof Service

```bash
cd toploc
docker-compose up -d
```

This starts the Flask API server on port 6500 that generates TOPLOC proofs.

### 3. Start the EigenLayer AVS DevNet

```bash
cd verifiable-benchmarks-avs
devkit avs build
devkit avs devnet start
```

This will:
- Deploy all smart contracts
- Register operators
- Start the aggregator and executor services
- Set up the full AVS infrastructure

### 4. Test the System

#### Using DevKit CLI

```bash
devkit avs call -- signature="(string,string)" args='("https://huggingface.co/benbencik/eigen-models/blob/main/SimpleNet_20250618210855.pt","https://huggingface.co/datasets/benbencik/eigen-datasets/blob/main/iris.csv")'
```

#### Using the Web Interface

```bash
cd ml-verification-interface
npm install
npm run dev
```

Visit `http://localhost:3000` to use the web interface for:
- Generating proofs
- Verifying existing proofs
- Viewing verification results

## 🔧 Detailed Setup Instructions

### EigenLayer AVS Configuration

The AVS is configured through two main files:

1. **`verifiable-benchmarks-avs/config/config.yaml`** - Project-level settings
2. **`verifiable-benchmarks-avs/config/contexts/devnet.yaml`** - Environment-specific settings

#### Key Configuration Options

```yaml
# In devnet.yaml
chains:
  l1:
    chain_id: 31337
    rpc_url: "http://localhost:8545"
    fork:
      block: 22475020
      url: ""  # Set in .env file
      block_time: 3
```

#### Available DevKit Commands

```bash
# Build contracts and binaries
devkit avs build

# Start local devnet
devkit avs devnet start

# Stop devnet
devkit avs devnet stop

# List running containers
devkit avs devnet list

# Test task execution
devkit avs call -- signature="(string,string)" args='("url1","url2")'

# View configuration
devkit avs config --list
devkit avs context --list
```

### TOPLOC Service Configuration

The TOPLOC service runs as a Docker container with the following configuration:

```yaml
# toploc/docker-compose.yml
services:
  toploc:
    build: .
    ports:
      - "6500:6500"
    environment:
      - PYTHONPATH=/app
```

#### API Endpoints

- **POST `/run`** - Generate or verify proofs
  - Parameters: `dataset_url`, `model_url`, `task` (predict/verify)
  - Returns: Proof string or verification result

### Web Interface Configuration

The web interface is a Next.js application with:

- **Frontend**: React + TypeScript + Tailwind CSS
- **API Routes**: `/api/toploc-proof` for proof generation
- **Port**: 3000 (default)

## 🧪 Testing and Development

### Manual Testing Workflow

1. **Start Services**:
   ```bash
   # Terminal 1: Start TOPLOC service
   cd toploc && docker-compose up -d
   
   # Terminal 2: Start AVS devnet
   cd verifiable-benchmarks-avs && devkit avs devnet start
   
   # Terminal 3: Start web interface
   cd ml-verification-interface && npm run dev
   ```

2. **Test Proof Generation**:
   ```bash
   # Using DevKit CLI
   devkit avs call -- signature="(string,string)" args='("https://defillama.com/chain/ethereum/modelUrl","https://defillama.com/chain/ethereum/dataUrl")'
   
   # Using web interface
   # Visit http://localhost:3000 and use the "Generate Proof" tab
   ```

3. **Test Proof Verification**:
   ```bash
   # Using web interface
   # Visit http://localhost:3000 and use the "Verify Proof" tab
   ```

### Development Workflow

#### Modifying AVS Logic

Edit `verifiable-benchmarks-avs/cmd/main.go`:
- `ValidateTask()` - Add custom validation logic
- `HandleTask()` - Modify task processing logic
- `toplocBenchmark()` - Customize benchmark parameters

#### Modifying TOPLOC Implementation

Edit `toploc/app.py`:
- Modify proof generation parameters
- Add new model/dataset support
- Customize verification logic

#### Modifying Web Interface

Edit `ml-verification-interface/app/`:
- `page.tsx` - Main interface
- `api/toploc-proof/route.ts` - API endpoint

## 📊 System Components

### Task Worker (AVS Performer)

The main AVS logic in `verifiable-benchmarks-avs/cmd/main.go`:

```go
type TaskWorker struct {
    logger *zap.Logger
}

func (tw *TaskWorker) HandleTask(t *performerV1.TaskRequest) (*performerV1.TaskResponse, error) {
    // 1. Call TOPLOC service to generate proof
    accuracy, proof, err := tw.toplocBenchmark()
    
    // 2. Create result object
    result := BenchmarkResult{
        ModelUrl: modelUrl,
        DataUrl:  datasetUrl,
        Accuracy: accuracy,
        Proof:    proof,
    }
    
    // 3. Upload to IPFS via Pinata
    cid, err := tw.uploadToPinata(result)
    
    // 4. Return ABI-encoded result
    return &performerV1.TaskResponse{
        TaskId: t.TaskId,
        Result: resultBytes,
    }, nil
}
```

### TOPLOC Proof Generation

The proof service in `toploc/app.py`:

```python
@app.route("/run", methods=["POST"])
def run_task():
    dataset_url = request.form.get("dataset_url")
    model_url = request.form.get("model_url")
    task = request.form.get("task")
    
    if task == "predict":
        prover = ModelProver(model)
        proof_data = prover.generate_proof(X, prover_params)
        return f'{proof_data["proofs_base64"]}\nAccuracy: 92%'
```

### Web Interface

The frontend in `ml-verification-interface/app/page.tsx`:

```typescript
const generateProof = async () => {
    const response = await fetch('/api/toploc-proof', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            modelUrl: 'https://defillama.com/chain/ethereum/modelUrl',
            dataUrl: 'https://defillama.com/chain/ethereum/dataUrl',
        }),
    })
    const data = await response.json()
    setProofData(data)
}
```

## 🔍 Troubleshooting

### Common Issues

1. **DevNet won't start**:
   - Ensure Docker is running
   - Check that fork URLs are set in `.env`
   - Verify all dependencies are installed

2. **TOPLOC service errors**:
   - Check Docker container logs: `docker-compose logs toploc`
   - Verify port 6500 is available
   - Check model/dataset URLs are accessible

3. **Web interface issues**:
   - Ensure Node.js dependencies are installed
   - Check for port conflicts on 3000
   - Verify API endpoints are responding

### Logs and Debugging

```bash
# AVS logs
devkit avs devnet list
docker logs <container_name>

# TOPLOC logs
cd toploc && docker-compose logs -f

# Web interface logs
cd ml-verification-interface && npm run dev
```

## 📚 References

- [TOPLOC: Polynomial Congruence Locality-Sensitive Hashing for Verifiable Neural Network Inference](https://arxiv.org/pdf/2501.16007)
- [EigenLayer Documentation](https://docs.eigenlayer.xyz/)
- [Hourglass AVS Framework](https://github.com/Layr-Labs/hourglass-avs-template)
- [DevKit CLI Documentation](https://github.com/Layr-Labs/devkit-cli)

## Contact
Ben: bejamin.bencik@tum-blockchain.com

Alex: alexander.semenov@tum-blockchain.com

Starting to build at "The Vault" by Eigenlayer in Berlin June 2025
