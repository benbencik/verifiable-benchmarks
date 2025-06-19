"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Shield, Terminal, Code } from "lucide-react"

interface ProofData {
  modelUrl: string
  datasetUrl: string
  proof: string
  merkleRoot: string
}

interface VerificationResult {
  valid: boolean
  actualAccuracy: string
  claimedAccuracy: string
  merkleRoot: string
  validatorConsensus: number
  details: string[]
}

export default function MLVerificationInterface() {
  const [mode, setMode] = useState<"generate" | "verify">("generate")

  // Generate mode state
  const [generateForm, setGenerateForm] = useState({
    modelUrl: "",
    datasetUrl: "",
  })
  const [proofData, setProofData] = useState<ProofData | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  // Verify mode state
  const [verifyForm, setVerifyForm] = useState({
    proof: "",
    modelUrl: "",
    datasetUrl: "",
  })
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null)
  const [isVerifying, setIsVerifying] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleGenerateInputChange = (field: string, value: string) => {
    setGenerateForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleVerifyInputChange = (field: string, value: string) => {
    setVerifyForm((prev) => ({ ...prev, [field]: value }))
  }

  const generateProof = async () => {
    setIsGenerating(true)
    setProgress(0)

    const steps = [
      "Loading model and dataset...",
      "Running inference...",
      "Computing activation hashes...",
      "Generating TOPLOC proof...",
      "Creating Merkle tree...",
      "Encoding proof...",
    ]

    for (let i = 0; i < steps.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 800))
      setProgress(((i + 1) / steps.length) * 100)
    }

    // Generate mock proof with realistic accuracy
    const mockAccuracy = (Math.random() * 10 + 90).toFixed(2) // 90-100%
    const mockProof = btoa(
      JSON.stringify({
        version: "toploc-v1.0",
        activationHashes: Array.from({ length: 10 }, () => Math.random().toString(36).substring(7)),
        topKIndices: Array.from({ length: 5 }, () => Math.floor(Math.random() * 1000)),
        polynomialCoeff: Math.random().toString(36).substring(7),
        modelHash: Math.random().toString(16).substring(2, 18),
        timestamp: Date.now(),
        accuracy: mockAccuracy,
        modelUrl: generateForm.modelUrl,
        datasetUrl: generateForm.datasetUrl,
      }),
    )

    const mockMerkleRoot = Array.from({ length: 8 }, () => Math.random().toString(16).substring(2, 10)).join("")

    setProofData({
      modelUrl: generateForm.modelUrl,
      datasetUrl: generateForm.datasetUrl,
      proof: mockProof,
      merkleRoot: mockMerkleRoot,
    })

    setIsGenerating(false)
    setProgress(0)
  }

  const verifyProof = async () => {
    if (!verifyForm.proof.trim() || !verifyForm.modelUrl.trim() || !verifyForm.datasetUrl.trim()) return

    setIsVerifying(true)
    setProgress(0)

    const verificationSteps = [
      "Parsing proof structure...",
      "Submitting to EigenLayer AVS...",
      "Validators recomputing inference...",
      "Checking TOPLOC encoding...",
      "Verifying Merkle inclusion...",
      "Reaching validator consensus...",
    ]

    for (let i = 0; i < verificationSteps.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setProgress(((i + 1) / verificationSteps.length) * 100)
    }

    try {
      const decodedProof = JSON.parse(atob(verifyForm.proof))
      const claimedAcc = decodedProof.accuracy || "95.00"
      const actualAcc = (Number.parseFloat(claimedAcc) + (Math.random() - 0.5) * 2).toFixed(2)
      const consensus = Math.floor(Math.random() * 20) + 80 // 80-100%

      // Check if URLs match
      const urlsMatch =
        decodedProof.modelUrl === verifyForm.modelUrl && decodedProof.datasetUrl === verifyForm.datasetUrl

      setVerificationResult({
        valid: urlsMatch && Math.random() > 0.2, // 80% chance of valid if URLs match
        actualAccuracy: actualAcc,
        claimedAccuracy: claimedAcc,
        merkleRoot: Array.from({ length: 8 }, () => Math.random().toString(16).substring(2, 10)).join(""),
        validatorConsensus: consensus,
        details: [
          urlsMatch ? "✓ Model URL matches" : "✗ Model URL mismatch",
          urlsMatch ? "✓ Dataset URL matches" : "✗ Dataset URL mismatch",
          "✓ Proof structure valid",
          "✓ LSH encoding verified",
          "✓ Polynomial congruence matches",
          "✓ Merkle inclusion confirmed",
          `✓ ${consensus}% validator consensus`,
        ],
      })
    } catch {
      setVerificationResult({
        valid: false,
        actualAccuracy: "N/A",
        claimedAccuracy: "N/A",
        merkleRoot: "Invalid",
        validatorConsensus: 0,
        details: ["✗ Invalid proof format", "✗ Base64 decoding failed", "✗ Malformed JSON structure"],
      })
    }

    setIsVerifying(false)
    setProgress(0)
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-slate-900">TOPLOC ML Verification</h1>
          <p className="text-slate-600 max-w-2xl mx-auto">
            Cryptographic verification of ML inference results using locality-sensitive hashing and EigenLayer AVS
          </p>
        </div>

        {/* Mode Selector */}
        <div className="flex justify-center">
          <div className="bg-white border border-slate-200 rounded-lg p-1 shadow-sm">
            <Button
              variant={mode === "generate" ? "default" : "ghost"}
              onClick={() => setMode("generate")}
              className={mode === "generate" ? "bg-blue-600 text-white" : "text-slate-600"}
            >
              Generate Proof
            </Button>
            <Button
              variant={mode === "verify" ? "default" : "ghost"}
              onClick={() => setMode("verify")}
              className={mode === "verify" ? "bg-blue-600 text-white" : "text-slate-600"}
            >
              Verify Proof
            </Button>
          </div>
        </div>

        {mode === "generate" ? (
          /* Generate Mode */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Form */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Terminal className="h-5 w-5" />
                  Generate Proof
                </CardTitle>
                <CardDescription>Provide your ML model and dataset URLs to generate a TOPLOC proof</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="modelUrl">Model URL</Label>
                  <Input
                    id="modelUrl"
                    placeholder="https://huggingface.co/model-name"
                    value={generateForm.modelUrl}
                    onChange={(e) => handleGenerateInputChange("modelUrl", e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="datasetUrl">Dataset URL</Label>
                  <Input
                    id="datasetUrl"
                    placeholder="https://datasets.com/test-set"
                    value={generateForm.datasetUrl}
                    onChange={(e) => handleGenerateInputChange("datasetUrl", e.target.value)}
                  />
                </div>

                <Button
                  onClick={generateProof}
                  disabled={!generateForm.modelUrl || !generateForm.datasetUrl || isGenerating}
                  className="w-full"
                >
                  {isGenerating ? "Generating Proof..." : "Generate TOPLOC Proof"}
                </Button>

                {isGenerating && (
                  <div className="space-y-2">
                    <Progress value={progress} />
                    <p className="text-sm text-slate-600 text-center">
                      Processing inference and generating cryptographic proof...
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Proof Output */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Generated Proof
                </CardTitle>
                <CardDescription>TOPLOC-encoded proof with Merkle tree aggregation</CardDescription>
              </CardHeader>
              <CardContent>
                {proofData ? (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Base64 Encoded Proof</Label>
                      <Textarea value={proofData.proof} readOnly className="font-mono text-xs" rows={4} />
                    </div>

                    <div className="space-y-2">
                      <Label>Merkle Root</Label>
                      <div className="font-mono text-xs bg-slate-100 p-2 rounded border">0x{proofData.merkleRoot}</div>
                    </div>

                    <div className="grid grid-cols-1 gap-2 text-sm">
                      <div>
                        <Label>Model URL</Label>
                        <p className="text-slate-600 text-xs break-all">{proofData.modelUrl}</p>
                      </div>
                      <div>
                        <Label>Dataset URL</Label>
                        <p className="text-slate-600 text-xs break-all">{proofData.datasetUrl}</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Generate a proof to see verification details</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ) : (
          /* Verify Mode */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Proof Input */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Verify Proof
                </CardTitle>
                <CardDescription>Provide proof and corresponding model/dataset URLs for verification</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Base64 Encoded Proof</Label>
                  <Textarea
                    className="font-mono text-xs"
                    placeholder="Paste base64 encoded TOPLOC proof here..."
                    value={verifyForm.proof}
                    onChange={(e) => handleVerifyInputChange("proof", e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="verifyModelUrl">Model URL</Label>
                  <Input
                    id="verifyModelUrl"
                    placeholder="https://huggingface.co/model-name"
                    value={verifyForm.modelUrl}
                    onChange={(e) => handleVerifyInputChange("modelUrl", e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="verifyDatasetUrl">Dataset URL</Label>
                  <Input
                    id="verifyDatasetUrl"
                    placeholder="https://datasets.com/test-set"
                    value={verifyForm.datasetUrl}
                    onChange={(e) => handleVerifyInputChange("datasetUrl", e.target.value)}
                  />
                </div>

                <Button
                  onClick={verifyProof}
                  disabled={
                    !verifyForm.proof.trim() ||
                    !verifyForm.modelUrl.trim() ||
                    !verifyForm.datasetUrl.trim() ||
                    isVerifying
                  }
                  className="w-full"
                >
                  {isVerifying ? "Verifying via EigenLayer AVS..." : "Verify Proof"}
                </Button>

                {isVerifying && (
                  <div className="space-y-2">
                    <Progress value={progress} />
                    <p className="text-sm text-slate-600 text-center">
                      EigenLayer validators are recomputing and verifying...
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Verification Result */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  Verification Result
                </CardTitle>
                <CardDescription>Results from EigenLayer AVS validation</CardDescription>
              </CardHeader>
              <CardContent>
                {verificationResult ? (
                  <div className="space-y-4">
                    <Alert
                      className={verificationResult.valid ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}
                    >
                      <AlertDescription>
                        <div className="font-semibold mb-2">
                          {verificationResult.valid ? "✓ Proof Verified Successfully" : "✗ Verification Failed"}
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Claimed:</span> {verificationResult.claimedAccuracy}%
                          </div>
                          <div>
                            <span className="font-medium">Verified:</span> {verificationResult.actualAccuracy}%
                          </div>
                        </div>
                      </AlertDescription>
                    </Alert>

                    <div className="space-y-2">
                      <Label>Validation Details</Label>
                      <div className="bg-slate-50 p-3 rounded text-sm space-y-1">
                        {verificationResult.details.map((detail, i) => (
                          <div key={i} className="font-mono text-xs">
                            {detail}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex justify-center">
                      <Badge variant={verificationResult.valid ? "default" : "destructive"}>
                        <CheckCircle className="h-3 w-3 mr-1" />
                        {verificationResult.valid ? "Cryptographically Verified" : "Verification Failed"}
                      </Badge>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Submit a proof for verification</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* System Overview */}
        <Card>
          <CardHeader>
            <CardTitle>How TOPLOC Works</CardTitle>
            <CardDescription>Locality-sensitive hashing with EigenLayer AVS verification</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                  <Terminal className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold">LSH Encoding</h3>
                <p className="text-sm text-slate-600">
                  Hash top-k activation values and encode as polynomial congruence for 1000x compression
                </p>
              </div>

              <div className="text-center space-y-2">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                  <Code className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold">Merkle Aggregation</h3>
                <p className="text-sm text-slate-600">
                  Bundle proofs into Merkle trees for efficient on-chain storage and batch verification
                </p>
              </div>

              <div className="text-center space-y-2">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                  <Shield className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold">EigenLayer AVS</h3>
                <p className="text-sm text-slate-600">
                  Decentralized validators verify proofs through independent recomputation
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
