package main

import (
	"context"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/rand"
	"time"

	"github.com/Layr-Labs/hourglass-monorepo/ponos/pkg/performer/server"
	performerV1 "github.com/Layr-Labs/protocol-apis/gen/protos/eigenlayer/hourglass/v1/performer"
	"go.uber.org/zap"
)

type TaskWorker struct {
	logger *zap.Logger
}

// This struct must match the one in your AVSTaskHook.sol contract
type BenchmarkTaskPayload struct {
	ModelUrl   string `json:"modelUrl"`
	DatasetUrl string `json:"datasetUrl"`
}

// Struct for the result to be returned to the contract
// proof can be any JSON-serializable object, here as map[string]interface{}
type BenchmarkResult struct {
	Proof    map[string]interface{} `json:"proof"`
	Accuracy uint8                  `json:"accuracy"`
}

func NewTaskWorker(logger *zap.Logger) *TaskWorker {
	return &TaskWorker{
		logger: logger,
	}
}

func (tw *TaskWorker) ValidateTask(t *performerV1.TaskRequest) error {
	tw.logger.Sugar().Infow("Validating task",
		zap.String("taskId", hex.EncodeToString(t.TaskId)),
		zap.Binary("taskData", t.Payload),
	)

	var payload BenchmarkTaskPayload
	if err := json.Unmarshal(t.Payload, &payload); err != nil {
		tw.logger.Error("Failed to unmarshal task data", zap.Error(err))
		return fmt.Errorf("invalid task data format: %w", err)
	}

	if payload.ModelUrl == "" || payload.DatasetUrl == "" {
		return fmt.Errorf("modelUrl and datasetUrl cannot be empty")
	}

	tw.logger.Sugar().Info("Task validation successful")
	return nil
}

// Here is the benchmarking function
func (tw *TaskWorker) toplocBenchmark(modelUrl, datasetUrl string) (uint8, map[string]interface{}, error) {
    // Simulate some processing time
    time.Sleep(2 * time.Second)

    // Generate a random accuracy between 85 and 99
    accuracy := uint8(85 + rand.Intn(15))

    // Create a mock proof
    proof := map[string]interface{}{
        "timestamp": time.Now().Unix(),
        "modelUrl":  modelUrl,
        "datasetUrl": datasetUrl,
        "details":   "This is a mock proof object",
    }
    return accuracy, proof, nil
}

func (tw *TaskWorker) HandleTask(t *performerV1.TaskRequest) (*performerV1.TaskResponse, error) {
	tw.logger.Sugar().Infow("Handling task",
		zap.String("taskId", hex.EncodeToString(t.TaskId)),
	)

	var payload BenchmarkTaskPayload
	if err := json.Unmarshal(t.Payload, &payload); err != nil {
		tw.logger.Error("HandleTask: Failed to unmarshal task data", zap.Error(err))
		return nil, fmt.Errorf("invalid task data format: %w", err)
	}

	tw.logger.Sugar().Infow("Starting benchmarking process...",
		zap.String("modelUrl", payload.ModelUrl),
		zap.String("datasetUrl", payload.DatasetUrl),
	)

	// Run the mock benchmark
	accuracy, proof, err := tw.toplocBenchmark(payload.ModelUrl, payload.DatasetUrl)
	if err != nil {
		tw.logger.Error("Benchmark failed", zap.Error(err))
		return nil, err
	}

	tw.logger.Sugar().Infow("Benchmarking completed",
		zap.String("modelUrl", payload.ModelUrl),
		zap.Uint8("accuracy", accuracy),
		zap.String("proof", proof),
	)


	result := BenchmarkResult{
		Proof:    proof,
		Accuracy: accuracy,
	}

	resultBytes, err := json.Marshal(result)
	if err != nil {
		tw.logger.Error("Failed to marshal result JSON", zap.Error(err))
		return nil, err
	}

	return &performerV1.TaskResponse{
		TaskId: t.TaskId,
		Result: resultBytes,
	}, nil
}

func main() {
	// Initialize random seed
	rand.Seed(time.Now().UnixNano())

	ctx := context.Background()
	l, _ := zap.NewProduction()

	w := NewTaskWorker(l)

	pp, err := server.NewPonosPerformerWithRpcServer(&server.PonosPerformerConfig{
		Port:    8080,
		Timeout: 5 * time.Second,
	}, w, l)
	if err != nil {
		panic(fmt.Errorf("failed to create performer: %w", err))
	}

	if err := pp.Start(ctx); err != nil {
		panic(err)
	}
}
