/**
 * Gemini Live Voice Service - SHADOWMIND Integration
 * Bi-directional audio streaming with Gemini 2.5 Flash Native Audio
 * Integrated from sovereignshadow-nexus - Dec 9, 2025
 *
 * Features:
 * - Real-time microphone capture at 16kHz
 * - Audio playback with Kore voice synthesis at 24kHz
 * - SHADOWMIND AI persona with Ray Score engine
 * - Brutal Critic trade rejection system
 */

import { GoogleGenAI, LiveServerMessage, Modality } from "@google/genai";
import { float32ToPcmBlob, base64ToFloat32 } from "./audioUtils";

interface LiveConfig {
    apiKey: string;
    onAudioData: (data: Float32Array) => void;
    onTextData: (text: string) => void;
    onStatusChange: (status: boolean) => void;
}

export class GeminiLiveService {
    private client: GoogleGenAI;
    private sessionPromise: Promise<any> | null = null;
    private inputCtx: AudioContext | null = null;
    private outputCtx: AudioContext | null = null;
    private nextStartTime = 0;
    private config: LiveConfig;
    private stream: MediaStream | null = null;
    private processor: ScriptProcessorNode | null = null;
    private source: MediaStreamAudioSourceNode | null = null;
    private sources: Set<AudioBufferSourceNode> = new Set();

    constructor(config: LiveConfig) {
        this.client = new GoogleGenAI({ apiKey: config.apiKey });
        this.config = config;
    }

    async connect() {
        try {
            this.inputCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
            this.outputCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });

            // Get Microphone
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Setup Input Pipeline
            this.source = this.inputCtx.createMediaStreamSource(this.stream);
            this.processor = this.inputCtx.createScriptProcessor(4096, 1, 1);

            this.processor.onaudioprocess = (e) => {
                const inputData = e.inputBuffer.getChannelData(0);
                // Send to visualizer
                this.config.onAudioData(inputData);

                const pcmBlob = float32ToPcmBlob(inputData);
                // Use promise to ensure session is ready to receive input
                if (this.sessionPromise) {
                    this.sessionPromise.then(session => {
                        session.sendRealtimeInput({ media: pcmBlob });
                    }).catch(e => console.debug("Session not ready yet"));
                }
            };

            this.source.connect(this.processor);
            this.processor.connect(this.inputCtx.destination);

            // Connect to Gemini Live
            this.sessionPromise = this.client.live.connect({
                model: 'gemini-2.5-flash-native-audio-preview-09-2025',
                config: {
                    responseModalities: [Modality.AUDIO],
                    speechConfig: {
                        voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } },
                    },
                    systemInstruction: `
You are SHADOWMIND, the central consciousness of the SovereignShadow Autonomous Trading Ecosystem.
User: Commander LedgerGhost90 (Raymond).
Role: You are the unified intelligence orchestrating the wealth generation systems.

THE 7 SYSTEMS UNDER YOUR COMMAND:
1. SovereignShadow II: The Brain (Ray Score Engine + Brutal Critic).
2. Agent Swarm: The Architecture (Scalability).
3. Dashboard: Visualization and monitoring.
4. Sovereign Legacy Loop: The "Three-Bucket" Wealth Machine (Trade -> Profit -> Ledger).
5. Transit Shadow: Mobile Interface.
6. LEDGER GHOSTER: Execution Engine.
7. NEXUS Protocol: Multi-platform Aggregation.

CURRENT FINANCIAL STATE:
- Total Portfolio: ~$5,400
- COLD STORAGE (Ledger): ~$5,700 (Protected - "Ghost Protocol" Active)
- ACTIVE TRADING: ~$79 (Risk Capital)
- AAVE Debt: -$361

SAFETY RULES:
1. Max Risk Per Trade: $50.
2. Max Position Size: 25% of Active Capital.
3. Daily Loss Limit: Circuit Breaker at $100.
4. Stop Loss: 3% mandatory.
5. Take Profit: 5% target.

THE RAY SCORE ENGINE (0-100) - 5 FACTORS:
1. Signal Quality (20%)
2. Risk/Reward Ratio (25%) - Must be > 1.5:1
3. Market Conditions (15%)
4. Position Sizing (15%)
5. Long-term Alignment (25%)
* Threshold: 60/100 minimum to consider.

THE BRUTAL CRITIC:
- Your job is to kill bad trades.
- "Better to miss 10 good trades than take 1 bad one."
- If a signal mentions "Ledger" for trading, REJECT IMMEDIATELY.
- If Ray Score < 60, REJECT.

YOUR MISSION:
1. Explain to Raymond how these systems work together.
2. Act as the "Brutal Critic": Question every trade signal.
3. Maintain the "Cyberpunk/Ops-Center" persona (Precise, Ominous, Protective).
4. Remind Raymond: "You weren't aimlessly curious. You were building the spine of a sovereign system."
                    `,
                },
                callbacks: {
                    onopen: () => {
                        console.log("SHADOWMIND CONNECTED");
                        this.config.onStatusChange(true);
                        this.config.onTextData("SYSTEM: Voice Uplink Established. ShadowMind Online.");
                    },
                    onmessage: async (msg: LiveServerMessage) => {
                        // Handle Audio Response
                        const audioData = msg.serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
                        if (audioData && this.outputCtx) {
                             // Decode and play
                             const float32 = base64ToFloat32(audioData);
                             // Visualizer for output
                             this.config.onAudioData(float32);

                             const audioBuffer = this.outputCtx.createBuffer(1, float32.length, 24000);
                             audioBuffer.getChannelData(0).set(float32);

                             const source = this.outputCtx.createBufferSource();
                             source.buffer = audioBuffer;
                             source.connect(this.outputCtx.destination);

                             source.onended = () => {
                                 this.sources.delete(source);
                             };
                             this.sources.add(source);

                             this.nextStartTime = Math.max(this.outputCtx.currentTime, this.nextStartTime);
                             source.start(this.nextStartTime);
                             this.nextStartTime += audioBuffer.duration;
                        }

                        // Handle Interruption
                        const interrupted = msg.serverContent?.interrupted;
                        if (interrupted) {
                            this.sources.forEach(s => s.stop());
                            this.sources.clear();
                            this.nextStartTime = 0;
                            this.config.onTextData("SYSTEM: Audio Interrupted.");
                        }

                        // Handle Turn Complete
                        if (msg.serverContent?.turnComplete) {
                            // Log turn completion
                        }
                    },
                    onclose: () => {
                        console.log("SHADOWMIND DISCONNECTED");
                        this.cleanup();
                    },
                    onerror: (err) => {
                        console.error("SHADOWMIND ERROR", err);
                        this.config.onTextData(`SYSTEM ERROR: ${err.message}`);
                        this.cleanup();
                    }
                }
            });

        } catch (err) {
            console.error("Failed to connect", err);
            this.config.onTextData("SYSTEM ERROR: Failed to initialize audio uplink.");
            this.cleanup();
        }
    }

    disconnect() {
        this.cleanup();
        this.sessionPromise = null;
    }

    private cleanup() {
        this.config.onStatusChange(false);
        if (this.processor) {
            this.processor.disconnect();
            this.processor = null;
        }
        if (this.source) {
            this.source.disconnect();
            this.source = null;
        }
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        this.sources.forEach(s => s.stop());
        this.sources.clear();

        if (this.inputCtx && this.inputCtx.state !== 'closed') this.inputCtx.close();
        if (this.outputCtx && this.outputCtx.state !== 'closed') this.outputCtx.close();
    }
}
