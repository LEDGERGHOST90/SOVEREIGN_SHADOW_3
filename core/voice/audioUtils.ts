/**
 * Audio Utilities for Gemini Live Voice Service
 * PCM encoding/decoding for bi-directional audio streaming
 * Integrated from sovereignshadow-nexus - Dec 9, 2025
 */

import { Blob } from '@google/genai';

export const audioContextOptions = {
    sampleRate: 16000, // Gemini Native Audio prefers 16kHz for input
};

/**
 * Decode base64 audio from Gemini to Float32Array waveform
 * @param base64 - Base64 encoded PCM audio from Gemini
 * @returns Float32Array suitable for AudioBuffer
 */
export function base64ToFloat32(base64: string): Float32Array {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    const int16 = new Int16Array(bytes.buffer);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) {
        float32[i] = int16[i] / 32768.0;
    }
    return float32;
}

/**
 * Encode Float32Array microphone data to PCM blob for Gemini
 * @param data - Float32Array from microphone
 * @returns Blob with base64 PCM data at 16kHz
 */
export function float32ToPcmBlob(data: Float32Array): Blob {
    const l = data.length;
    const int16 = new Int16Array(l);
    for (let i = 0; i < l; i++) {
        // Clamp values to [-1, 1] before converting
        const s = Math.max(-1, Math.min(1, data[i]));
        int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    // Manual base64 encoding for Uint8Array
    let binary = '';
    const bytes = new Uint8Array(int16.buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }

    return {
        data: btoa(binary),
        mimeType: 'audio/pcm;rate=16000',
    };
}

/**
 * Create dual audio contexts for input (16kHz) and output (24kHz)
 * Gemini outputs at 24kHz, inputs prefer 16kHz
 */
export async function createAudioContexts() {
    const inputCtx = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000,
    });
    const outputCtx = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 24000, // Gemini output is often 24kHz
    });
    return { inputCtx, outputCtx };
}
