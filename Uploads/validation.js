/**
 * Validation utilities for NEXUS Protocol
 */

export const isEmail = (v) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v);
export const isStrongEnough = (v) => v.length >= 8;

