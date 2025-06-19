package main

import (
	"context"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/rand"
	"strings"
	"time"
	"bytes"
	"net/http"
	"mime/multipart"
	"github.com/Layr-Labs/hourglass-monorepo/ponos/pkg/performer/server"
	performerV1 "github.com/Layr-Labs/protocol-apis/gen/protos/eigenlayer/hourglass/v1/performer"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"go.uber.org/zap"
	"github.com/mr-tron/base58"
	"io/ioutil"
	"crypto/tls"
)

type TaskWorker struct {
	logger *zap.Logger
}

type BenchmarkResult struct {
	ModelUrl string `json:"modelUrl"`
	DataUrl  string `json:"dataUrl"`
	Accuracy uint8  `json:"accuracy"`
	Proof    string `json:"proof"`
}

func NewTaskWorker(logger *zap.Logger) *TaskWorker {
	return &TaskWorker{
		logger: logger,
	}
}

func (tw *TaskWorker) ValidateTask(t *performerV1.TaskRequest) error {
	tw.logger.Sugar().Infow("[ValidateTask] Start",
		zap.String("taskId", hex.EncodeToString(t.TaskId)),
	)
	// No validation needed since we're not using parameters
	return nil
}

func (tw *TaskWorker) toplocBenchmark() (uint8, string, error) {
	// Hardcoded URLs for now since parameter transfer from contract here is not working fully yet because of ABI encoding issues
	modelUrl := "https://huggingface.co/benbencik/eigen-models/blob/main/SimpleNet_20250618210855.pt"
	datasetUrl := "https://huggingface.co/datasets/benbencik/eigen-datasets/blob/main/iris.csv"

	tw.logger.Sugar().Infow("[toplocBenchmark] Benchmarking started",
		zap.String("modelUrl", modelUrl),
		zap.String("datasetUrl", datasetUrl),
	)
	// calling the script to run the benchmark
	accuracy := uint8(0)
	
	proof := fmt.Sprintf("Proof for model %s and dataset %s at %d", modelUrl, datasetUrl, time.Now().Unix())
	tw.logger.Sugar().Infow("[toplocBenchmark] Benchmarking finished",
		zap.Uint8("accuracy", accuracy),
		zap.String("proof", proof),
	)
	return accuracy, proof, nil
}

func (w *TaskWorker) uploadToPinata(result BenchmarkResult) (string, error) {
	w.logger.Info("[uploadToPinata] Preparing to upload result to Pinata",
		zap.String("modelUrl", result.ModelUrl),
		zap.String("dataUrl", result.DataUrl),
	)

	// Create a buffer to store our multipart form data
	var b bytes.Buffer
	writer := multipart.NewWriter(&b)

	// Add the file
	part, err := writer.CreateFormFile("file", "benchmark_result.json")
	if err != nil {
		w.logger.Error("[uploadToPinata] Failed to create form file", zap.Error(err))
		return "", fmt.Errorf("failed to create form file: %w", err)
	}

	// Marshal the result to JSON
	resultJSON, err := json.Marshal(result)
	if err != nil {
		w.logger.Error("[uploadToPinata] Failed to marshal result", zap.Error(err))
		return "", fmt.Errorf("failed to marshal result: %w", err)
	}

	// Write the JSON to the form
	if _, err := part.Write(resultJSON); err != nil {
		w.logger.Error("[uploadToPinata] Failed to write result to form", zap.Error(err))
		return "", fmt.Errorf("failed to write result to form: %w", err)
	}

	// Add pinataMetadata
	metadata := map[string]interface{}{
		"name": "benchmark_result.json",
	}
	metadataJSON, err := json.Marshal(metadata)
	if err != nil {
		w.logger.Error("[uploadToPinata] Failed to marshal metadata", zap.Error(err))
		return "", fmt.Errorf("failed to marshal metadata: %w", err)
	}
	if err := writer.WriteField("pinataMetadata", string(metadataJSON)); err != nil {
		w.logger.Error("[uploadToPinata] Failed to write metadata field", zap.Error(err))
		return "", fmt.Errorf("failed to write metadata field: %w", err)
	}

	// Add pinataOptions
	options := map[string]interface{}{
		"cidVersion": 1,
	}
	optionsJSON, err := json.Marshal(options)
	if err != nil {
		w.logger.Error("[uploadToPinata] Failed to marshal options", zap.Error(err))
		return "", fmt.Errorf("failed to marshal options: %w", err)
	}
	if err := writer.WriteField("pinataOptions", string(optionsJSON)); err != nil {
		w.logger.Error("[uploadToPinata] Failed to write options field", zap.Error(err))
		return "", fmt.Errorf("failed to write options field: %w", err)
	}

	// Close the writer
	if err := writer.Close(); err != nil {
		w.logger.Error("[uploadToPinata] Failed to close writer", zap.Error(err))
		return "", fmt.Errorf("failed to close writer: %w", err)
	}

	// Create the request
	req, err := http.NewRequest("POST", "https://api.pinata.cloud/pinning/pinFileToIPFS", &b)
	if err != nil {
		w.logger.Error("[uploadToPinata] Failed to create request", zap.Error(err))
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	// Hardcoded JWT token
	jwt := ""

	// Set headers
	req.Header.Set("Authorization", "Bearer "+jwt)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	w.logger.Info("[uploadToPinata] Sending request to Pinata")

	// Create a custom HTTP client that skips TLS verification
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	// Send the request
	resp, err := client.Do(req)
	if err != nil {
		w.logger.Error("[uploadToPinata] Failed to send request", zap.Error(err))
		return "", fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	// Read the response
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		w.logger.Error("[uploadToPinata] Failed to read response", zap.Error(err))
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	// Check response status
	if resp.StatusCode != http.StatusOK {
		w.logger.Error("[uploadToPinata] Pinata error",
			zap.Int("statusCode", resp.StatusCode),
			zap.String("response", string(body)),
		)
		return "", fmt.Errorf("Pinata error: %s", string(body))
	}

	// Parse the response
	var response struct {
		IpfsHash string `json:"IpfsHash"`
	}
	if err := json.Unmarshal(body, &response); err != nil {
		w.logger.Error("[uploadToPinata] Failed to parse response", zap.Error(err))
		return "", fmt.Errorf("failed to parse response: %w", err)
	}

	w.logger.Info("[uploadToPinata] Successfully uploaded to Pinata",
		zap.String("ipfsHash", response.IpfsHash),
	)

	return response.IpfsHash, nil
}

func (tw *TaskWorker) HandleTask(t *performerV1.TaskRequest) (*performerV1.TaskResponse, error) {
	tw.logger.Sugar().Infow("[HandleTask] Start",
		zap.String("taskId", hex.EncodeToString(t.TaskId)),
	)

	// Hardcoded URLs for now since parameter transfer from contract here is not working fully yet because of ABI encoding issues
	modelUrl := "https://huggingface.co/benbencik/eigen-models/blob/main/SimpleNet_20250618210855.pt"
	datasetUrl := "https://huggingface.co/datasets/benbencik/eigen-datasets/blob/main/iris.csv"

	accuracy, proof, err := tw.toplocBenchmark()
	if err != nil {
		tw.logger.Error("[HandleTask] Benchmark failed", zap.Error(err))
		return nil, err
	}

	result := BenchmarkResult{
		ModelUrl: modelUrl,
		DataUrl:  datasetUrl,
		Accuracy: accuracy,
		Proof:    proof,
	}

	tw.logger.Info("[HandleTask] Uploading result to Pinata")
	cid, err := tw.uploadToPinata(result)
	if err != nil {
		tw.logger.Error("[HandleTask] Failed to upload result to Pinata", zap.Error(err))
		return nil, err
	}
	tw.logger.Sugar().Infow("[HandleTask] Uploaded result to Pinata", zap.String("cid", cid))

	cidBytes, err := cidToBytes32(cid)
	if err != nil {
		tw.logger.Error("[HandleTask] Failed to convert CID to bytes32", zap.Error(err))
		return nil, err
	}

	const cidABI = `[{"type":"tuple","components":[{"name":"ipfsCID","type":"bytes32"}]}]`
	parsedABI, err := abi.JSON(strings.NewReader(cidABI))
	if err != nil {
		tw.logger.Error("[HandleTask] Failed to parse ABI for CID", zap.Error(err))
		return nil, err
	}
	resultBytes, err := parsedABI.Pack("", cidBytes)
	if err != nil {
		tw.logger.Error("[HandleTask] Failed to ABI-encode CID", zap.Error(err))
		return nil, err
	}

	tw.logger.Sugar().Infow("[HandleTask] Task completed successfully",
		zap.String("taskId", hex.EncodeToString(t.TaskId)),
		zap.String("cid", cid),
	)

	return &performerV1.TaskResponse{
		TaskId: t.TaskId,
		Result: resultBytes,
	}, nil
}

// cidToBytes32 converts a base58 CIDv0 to a bytes32 (sha256 digest)
func cidToBytes32(cid string) ([32]byte, error) {
	var out [32]byte
	if len(cid) == 46 && strings.HasPrefix(cid, "Qm") {
		decoded, err := base58.Decode(cid)
		if err != nil {
			return out, err
		}
		if len(decoded) != 34 {
			return out, fmt.Errorf("unexpected multihash length: %d", len(decoded))
		}
		copy(out[:], decoded[2:])
		return out, nil
	}
	return out, fmt.Errorf("unsupported CID format: %s", cid)
}

func main() {
	rand.Seed(time.Now().UnixNano())

	ctx := context.Background()
	l, err := zap.NewProduction()
	if err != nil {
		fmt.Printf("Failed to create logger: %v\n", err)
		return
	}
	defer l.Sync()

	l.Info("[main] Starting TaskWorker performer")
	w := NewTaskWorker(l)

	l.Info("[main] Initializing PonosPerformerWithRpcServer")
	pp, err := server.NewPonosPerformerWithRpcServer(&server.PonosPerformerConfig{
		Port:    8080,
		Timeout: 5 * time.Second,
	}, w, l)
	if err != nil {
		l.Fatal("[main] failed to create performer", zap.Error(err))
	}

	l.Info("[main] Starting performer server loop")
	if err := pp.Start(ctx); err != nil {
		l.Fatal("[main] performer server exited with error", zap.Error(err))
	}
}
