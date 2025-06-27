# Trustless verification of machine learning inference

**Verifiable Benchmarks** is an open-source framework for trustless verification of machine learning inference, inspired by the [TOPLOC](https://arxiv.org/pdf/2501.16007) approach. This project addresses the critical challenge of establishing trust in third-party ML inference providers, ensuring that users can independently verify the integrity and faithfulness of off-chain model execution.

For more information about the project, take a look at the [Vault Hacker House Presentation](https://github.com/benbencik/verifiable-benchmarks/blob/main/Verifiable%20Benchmarks.pdf).


## Quick Start

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

Go to localhost `http://localhost:3000` to use the web interface for:
- Generating proofs
- Verifying existing proofs
- Viewing verification results


## Testing and Development

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

## System Components

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

## Contact
Ben: bejamin.bencik@tum-blockchain.com

Alex: alexander.semenov@tum-blockchain.com

Starting to build at "The Vault" by Eigenlayer in Berlin June 2025
