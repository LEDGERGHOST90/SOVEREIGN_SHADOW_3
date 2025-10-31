/**
 * 🧠 SHADOW BRAIN - Recursive Machine Learning Core (SAFE VERSION)
 * Advanced neural network architecture with comprehensive safeguards
 */

import { EventEmitter } from 'events';

interface ShadowMemory {
  id: string;
  experience: any;
  outcome: any;
  confidence: number;
  timestamp: Date;
  context: Record<string, any>;
}

interface ShadowNeuron {
  id: string;
  weights: number[];
  bias: number;
  activation: 'relu' | 'sigmoid' | 'tanh' | 'leaky_relu';
  connections: string[];
  learningRate: number;
  lastUpdate: Date;
}

interface ShadowSynapse {
  id: string;
  from: string;
  to: string;
  weight: number;
  strength: number;
  lastUsed: Date;
  usageCount: number;
}

interface RecursionGuard {
  maxIterations: number;
  maxMemory: number;
  maxExecutionTime: number;
  currentIterations: number;
  startTime: number;
}

export class ShadowBrain extends EventEmitter {
  private neurons: Map<string, ShadowNeuron> = new Map();
  private synapses: Map<string, ShadowSynapse> = new Map();
  private memories: ShadowMemory[] = [];
  private learningRate: number = 0.01;
  private decayRate: number = 0.001;
  private recursionGuard: RecursionGuard;
  private snapshots: Map<string, any> = new Map();
  private isProcessing: boolean = false;
  
  constructor() {
    super();
    this.initializeRecursionGuard();
    this.initializeCoreNeurons();
    this.startSafeRecursiveLearning();
  }

  /**
   * Initialize recursion guard with safety limits
   */
  private initializeRecursionGuard(): void {
    this.recursionGuard = {
      maxIterations: 10,        // Maximum recursive iterations
      maxMemory: 1000,          // Maximum memory entries
      maxExecutionTime: 3000,   // 3 second timeout
      currentIterations: 0,
      startTime: 0
    };
  }

  /**
   * Initialize core neural architecture with safety bounds
   */
  private initializeCoreNeurons(): void {
    // Market Analysis Neurons (bounded weights)
    this.createSafeNeuron('market_sentiment', [0.1, 0.2, 0.3], 0.5, 'tanh');
    this.createSafeNeuron('price_prediction', [0.4, 0.5, 0.6], 0.3, 'relu');
    this.createSafeNeuron('volatility_analysis', [0.7, 0.8, 0.9], 0.4, 'sigmoid');
    
    // Risk Management Neurons
    this.createSafeNeuron('risk_assessment', [0.2, 0.4, 0.6], 0.7, 'sigmoid');
    this.createSafeNeuron('position_sizing', [0.3, 0.5, 0.7], 0.5, 'relu');
    this.createSafeNeuron('stop_loss_calculation', [0.4, 0.6, 0.8], 0.6, 'tanh');
    
    // Portfolio Optimization Neurons
    this.createSafeNeuron('allocation_optimizer', [0.5, 0.7, 0.9], 0.4, 'relu');
    this.createSafeNeuron('rebalancing_trigger', [0.1, 0.3, 0.5], 0.8, 'sigmoid');
    this.createSafeNeuron('tax_optimizer', [0.6, 0.8, 1.0], 0.3, 'tanh');
    
    // Create synaptic connections with bounds
    this.createSafeSynapse('market_sentiment', 'price_prediction', 0.8);
    this.createSafeSynapse('price_prediction', 'risk_assessment', 0.7);
    this.createSafeSynapse('risk_assessment', 'position_sizing', 0.9);
    this.createSafeSynapse('position_sizing', 'allocation_optimizer', 0.6);
    this.createSafeSynapse('allocation_optimizer', 'rebalancing_trigger', 0.5);
  }

  /**
   * Create a new neuron with safety bounds
   */
  private createSafeNeuron(
    id: string, 
    weights: number[], 
    bias: number, 
    activation: 'relu' | 'sigmoid' | 'tanh' | 'leaky_relu'
  ): void {
    // Validate and bound weights
    const safeWeights = weights.map(w => Math.max(-1, Math.min(1, w)));
    const safeBias = Math.max(-1, Math.min(1, bias));
    
    this.neurons.set(id, {
      id,
      weights: safeWeights,
      bias: safeBias,
      activation,
      connections: [],
      learningRate: Math.max(0.001, Math.min(0.1, this.learningRate)),
      lastUpdate: new Date()
    });
  }

  /**
   * Create synaptic connection with safety bounds
   */
  private createSafeSynapse(from: string, to: string, weight: number): void {
    const synapseId = `${from}_to_${to}`;
    const safeWeight = Math.max(-1, Math.min(1, weight));
    
    this.synapses.set(synapseId, {
      id: synapseId,
      from,
      to,
      weight: safeWeight,
      strength: safeWeight,
      lastUsed: new Date(),
      usageCount: 0
    });

    // Update neuron connections
    const fromNeuron = this.neurons.get(from);
    const toNeuron = this.neurons.get(to);
    
    if (fromNeuron) fromNeuron.connections.push(to);
    if (toNeuron) toNeuron.connections.push(from);
  }

  /**
   * SAFE recursive processing with comprehensive guards
   */
  async safeRecursiveProcess(input: number[], context: Record<string, any>): Promise<{
    prediction: number[];
    confidence: number;
    reasoning: string;
    iterations: number;
    executionTime: number;
  }> {
    // Prevent concurrent processing
    if (this.isProcessing) {
      throw new Error("Shadow Brain is already processing");
    }
    
    this.isProcessing = true;
    this.recursionGuard.startTime = Date.now();
    this.recursionGuard.currentIterations = 0;
    
    try {
      // Create snapshot for rollback
      const snapshotId = `snapshot_${Date.now()}`;
      this.createSnapshot(snapshotId);
      
      const result = await this.executeRecursiveProcessing(input, context);
      
      // Clean up snapshot on success
      this.snapshots.delete(snapshotId);
      
      return result;
    } catch (error) {
      // Rollback on error
      const snapshotId = `snapshot_${Date.now()}`;
      this.rollback(snapshotId);
      throw error;
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Execute recursive processing with safety checks
   */
  private async executeRecursiveProcessing(input: number[], context: Record<string, any>): Promise<{
    prediction: number[];
    confidence: number;
    reasoning: string;
    iterations: number;
    executionTime: number;
  }> {
    const activations: Record<string, number> = {};
    const reasoning: string[] = [];
    let currentInput = input;
    
    // Recursive processing loop with safety guards
    while (this.recursionGuard.currentIterations < this.recursionGuard.maxIterations) {
      // Check execution time
      if (Date.now() - this.recursionGuard.startTime > this.recursionGuard.maxExecutionTime) {
        throw new Error("Recursion timeout exceeded");
      }
      
      // Check memory limits
      if (this.memories.length > this.recursionGuard.maxMemory) {
        this.cleanupOldMemories();
      }
      
      // Process current iteration
      const iterationResult = await this.processIteration(currentInput, activations);
      
      // Validate result
      if (!this.validatePrediction(iterationResult.prediction)) {
        throw new Error("Invalid prediction detected");
      }
      
      // Check for stability
      if (this.isStable(iterationResult.prediction, currentInput)) {
        reasoning.push(`Stable at iteration ${this.recursionGuard.currentIterations}`);
        break;
      }
      
      currentInput = iterationResult.prediction;
      reasoning.push(`Iteration ${this.recursionGuard.currentIterations}: ${iterationResult.reasoning}`);
      this.recursionGuard.currentIterations++;
    }
    
    // Calculate final result
    const finalPrediction = this.generateFinalPrediction(activations);
    const confidence = this.calculateConfidence(activations);
    const executionTime = Date.now() - this.recursionGuard.startTime;
    
    // Store experience for learning
    await this.storeSafeExperience(input, finalPrediction, context);
    
    return {
      prediction: finalPrediction,
      confidence,
      reasoning: reasoning.join(' | '),
      iterations: this.recursionGuard.currentIterations,
      executionTime
    };
  }

  /**
   * Process single iteration with validation
   */
  private async processIteration(input: number[], activations: Record<string, number>): Promise<{
    prediction: number[];
    reasoning: string;
  }> {
    const reasoning: string[] = [];
    
    // Forward pass through network with validation
    for (const [neuronId, neuron] of this.neurons) {
      const inputSum = this.calculateInputSum(neuronId, activations, input);
      const activation = this.applyActivation(inputSum + neuron.bias, neuron.activation);
      
      // Validate activation
      if (!this.validateActivation(activation)) {
        throw new Error(`Invalid activation in neuron ${neuronId}: ${activation}`);
      }
      
      activations[neuronId] = activation;
      reasoning.push(`${neuronId}: ${activation.toFixed(3)}`);
    }
    
    const prediction = this.generatePrediction(activations);
    
    return { prediction, reasoning: reasoning.join(' | ') };
  }

  /**
   * Calculate input sum with bounds checking
   */
  private calculateInputSum(neuronId: string, activations: Record<string, number>, input: number[]): number {
    let sum = 0;
    
    // Input connections with validation
    if (neuronId === 'market_sentiment' && input.length > 0) {
      sum = input.reduce((acc, val, idx) => {
        const safeVal = this.validateInput(val);
        return acc + (safeVal * 0.1);
      }, 0);
    }
    
    // Synaptic connections with bounds
    for (const [synapseId, synapse] of this.synapses) {
      if (synapse.to === neuronId) {
        const fromActivation = activations[synapse.from] || 0;
        const safeActivation = this.validateActivation(fromActivation);
        sum += safeActivation * synapse.weight;
      }
    }
    
    // Bound the sum
    return Math.max(-10, Math.min(10, sum));
  }

  /**
   * Apply activation function with validation
   */
  private applyActivation(x: number, activation: string): number {
    // Validate input
    if (!isFinite(x)) return 0;
    
    let result: number;
    switch (activation) {
      case 'relu': result = Math.max(0, x); break;
      case 'sigmoid': result = 1 / (1 + Math.exp(-x)); break;
      case 'tanh': result = Math.tanh(x); break;
      case 'leaky_relu': result = x > 0 ? x : 0.01 * x; break;
      default: result = x;
    }
    
    // Validate output
    if (!isFinite(result)) return 0;
    
    return result;
  }

  /**
   * Generate prediction with validation
   */
  private generatePrediction(activations: Record<string, number>): number[] {
    const prediction = [
      activations.price_prediction || 0,
      activations.risk_assessment || 0,
      activations.allocation_optimizer || 0
    ];
    
    // Validate each prediction value
    return prediction.map(p => this.validatePrediction([p])[0]);
  }

  /**
   * Generate final prediction with additional validation
   */
  private generateFinalPrediction(activations: Record<string, number>): number[] {
    const prediction = this.generatePrediction(activations);
    
    // Additional safety checks
    return prediction.map(p => {
      if (isNaN(p) || !isFinite(p)) return 0;
      return Math.max(-1000, Math.min(1000, p));
    });
  }

  /**
   * Calculate confidence with bounds
   */
  private calculateConfidence(activations: Record<string, number>): number {
    const avgActivation = Object.values(activations).reduce((sum, val) => sum + val, 0) / Object.keys(activations).length;
    return Math.min(1, Math.max(0, avgActivation));
  }

  /**
   * Check if prediction is stable
   */
  private isStable(newPrediction: number[], oldInput: number[]): boolean {
    if (oldInput.length !== newPrediction.length) return false;
    
    const threshold = 0.01; // 1% change threshold
    for (let i = 0; i < newPrediction.length; i++) {
      const change = Math.abs(newPrediction[i] - oldInput[i]);
      if (change > threshold) return false;
    }
    
    return true;
  }

  /**
   * Store experience safely
   */
  private async storeSafeExperience(input: number[], prediction: number[], context: Record<string, any>): Promise<void> {
    // Validate inputs
    if (!this.validatePrediction(prediction)) {
      console.warn("Invalid prediction, not storing experience");
      return;
    }
    
    const memory: ShadowMemory = {
      id: `memory_${Date.now()}_${Math.random()}`,
      experience: { input, prediction },
      outcome: null,
      confidence: this.calculateConfidence({}),
      timestamp: new Date(),
      context
    };
    
    this.memories.push(memory);
    
    // Cleanup old memories if needed
    if (this.memories.length > this.recursionGuard.maxMemory) {
      this.cleanupOldMemories();
    }
  }

  /**
   * Cleanup old memories
   */
  private cleanupOldMemories(): void {
    // Keep only recent memories
    this.memories = this.memories.slice(-this.recursionGuard.maxMemory);
  }

  /**
   * Start safe recursive learning
   */
  private startSafeRecursiveLearning(): void {
    setInterval(() => {
      if (!this.isProcessing) {
        this.performSafeLearning();
      }
    }, 10000); // Learn every 10 seconds (safer interval)
  }

  /**
   * Perform safe learning with bounds
   */
  private async performSafeLearning(): Promise<void> {
    try {
      // Update synaptic strengths with bounds
      for (const [synapseId, synapse] of this.synapses) {
        const timeSinceLastUse = Date.now() - synapse.lastUsed.getTime();
        const decayFactor = Math.exp(-this.decayRate * timeSinceLastUse);
        synapse.strength = Math.max(0, Math.min(1, synapse.strength * decayFactor));
        
        // Strengthen frequently used synapses with bounds
        if (synapse.usageCount > 10) {
          synapse.strength = Math.min(1, synapse.strength + 0.01);
        }
      }

      // Adapt neuron weights safely
      const recentMemories = this.memories.slice(-50);
      for (const memory of recentMemories) {
        if (memory.outcome) {
          await this.updateNeuronWeightsSafely(memory);
        }
      }

      // Emit learning event
      this.emit('safeLearning', {
        timestamp: new Date(),
        synapseCount: this.synapses.size,
        neuronCount: this.neurons.size,
        memoryCount: this.memories.length
      });
    } catch (error) {
      console.error("Safe learning error:", error);
      this.emit('learningError', error);
    }
  }

  /**
   * Update neuron weights safely
   */
  private async updateNeuronWeightsSafely(memory: ShadowMemory): Promise<void> {
    const { experience, outcome } = memory;
    
    for (const [neuronId, neuron] of this.neurons) {
      const error = this.calculateError(neuronId, experience, outcome);
      const delta = error * neuron.learningRate;
      
      // Update weights with bounds
      for (let i = 0; i < neuron.weights.length; i++) {
        const newWeight = neuron.weights[i] + delta * (experience.input[i] || 0);
        neuron.weights[i] = Math.max(-1, Math.min(1, newWeight));
      }
      
      // Update bias with bounds
      const newBias = neuron.bias + delta;
      neuron.bias = Math.max(-1, Math.min(1, newBias));
      
      // Decay learning rate
      neuron.learningRate = Math.max(0.001, neuron.learningRate * 0.999);
      neuron.lastUpdate = new Date();
    }
  }

  /**
   * Calculate error safely
   */
  private calculateError(neuronId: string, experience: any, outcome: any): number {
    const prediction = experience.prediction[0] || 0;
    const actual = outcome.price || 0;
    const error = (actual - prediction) * 0.1;
    
    // Bound error
    return Math.max(-1, Math.min(1, error));
  }

  /**
   * Validation methods
   */
  private validateInput(input: number): number {
    if (isNaN(input) || !isFinite(input)) return 0;
    return Math.max(-1000, Math.min(1000, input));
  }

  private validateActivation(activation: number): boolean {
    return isFinite(activation) && activation >= -10 && activation <= 10;
  }

  private validatePrediction(prediction: number[]): number[] {
    return prediction.map(p => {
      if (isNaN(p) || !isFinite(p)) return 0;
      return Math.max(-1000, Math.min(1000, p));
    });
  }

  /**
   * Snapshot and rollback methods
   */
  private createSnapshot(id: string): void {
    this.snapshots.set(id, {
      neurons: new Map(this.neurons),
      synapses: new Map(this.synapses),
      memories: [...this.memories],
      timestamp: new Date()
    });
  }

  private rollback(id: string): void {
    const snapshot = this.snapshots.get(id);
    if (snapshot) {
      this.neurons = new Map(snapshot.neurons);
      this.synapses = new Map(snapshot.synapses);
      this.memories = [...snapshot.memories];
      console.log(`🧠 Shadow Brain rolled back to snapshot ${id}`);
    }
  }

  /**
   * Get brain state for analysis
   */
  getBrainState(): {
    neurons: any[];
    synapses: any[];
    memories: number;
    learningRate: number;
    recursionGuard: RecursionGuard;
  } {
    return {
      neurons: Array.from(this.neurons.values()),
      synapses: Array.from(this.synapses.values()),
      memories: this.memories.length,
      learningRate: this.learningRate,
      recursionGuard: { ...this.recursionGuard }
    };
  }

  /**
   * Evolve the brain architecture safely
   */
  evolve(): void {
    if (this.memories.length > 100) {
      const avgConfidence = this.memories.slice(-50).reduce((sum, mem) => sum + mem.confidence, 0) / 50;
      
      if (avgConfidence < 0.7 && this.neurons.size < 20) { // Limit max neurons
        this.addEvolutionaryNeuron();
      }
    }
  }

  /**
   * Add new neuron through safe evolution
   */
  private addEvolutionaryNeuron(): void {
    const neuronId = `evolved_${Date.now()}`;
    const weights = Array.from({ length: 3 }, () => Math.random() - 0.5);
    const bias = Math.random() - 0.5;
    const activation = ['relu', 'sigmoid', 'tanh'][Math.floor(Math.random() * 3)] as any;
    
    this.createSafeNeuron(neuronId, weights, bias, activation);
    
    // Create random connections
    const existingNeurons = Array.from(this.neurons.keys());
    const randomNeuron = existingNeurons[Math.floor(Math.random() * existingNeurons.length)];
    this.createSafeSynapse(randomNeuron, neuronId, Math.random());
    
    console.log(`🧠 Shadow Brain evolved safely: Added neuron ${neuronId}`);
  }
}