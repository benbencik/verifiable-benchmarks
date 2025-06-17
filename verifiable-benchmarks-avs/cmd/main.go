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
	ModelId   string `json:"modelId"`
	DatasetId string `json:"datasetId"`
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

	if payload.ModelId == "" || payload.DatasetId == "" {
		return fmt.Errorf("modelId and datasetId cannot be empty")
	}

	tw.logger.Sugar().Info("Task validation successful")
	return nil
}

// mockBenchmark simulates running a benchmark on an AI model
func (tw *TaskWorker) mockBenchmark(modelId, datasetId string) (uint8, error) {
	// Simulate some processing time
	time.Sleep(2 * time.Second)

	// Generate a random accuracy between 85 and 99
	accuracy := uint8(85 + rand.Intn(15))

	// Simulate occasional failures
	if rand.Float32() < 0.1 { // 10% chance of failure
		return 0, fmt.Errorf("benchmark failed for model %s on dataset %s", modelId, datasetId)
	}

	return accuracy, nil
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

	tw.logger.Sugar().Infow("Starting benchmark",
		zap.String("modelId", payload.ModelId),
		zap.String("datasetId", payload.DatasetId),
	)

	// Run the mock benchmark
	accuracy, err := tw.mockBenchmark(payload.ModelId, payload.DatasetId)
	if err != nil {
		tw.logger.Error("Benchmark failed", zap.Error(err))
		return nil, err
	}

	tw.logger.Sugar().Infow("Benchmark completed",
		zap.String("modelId", payload.ModelId),
		zap.Uint8("accuracy", accuracy),
	)

	// Convert accuracy to a single byte
	resultBytes := []byte{accuracy}

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
