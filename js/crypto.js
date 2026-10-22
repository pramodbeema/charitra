/**
 * CHARITRA Crypto Module
 * AES-256-GCM encryption using Web Crypto API.
 * All vault data stored in Chrome storage is encrypted.
 * Raw keys are never stored — only the salt + derived key material.
 */

const PBKDF2_ITERATIONS = 310000; // OWASP 2023 recommended
const SALT_LENGTH = 16;
const IV_LENGTH = 12;
const KEY_LENGTH = 256;

/**
 * Derive a CryptoKey from a password + salt using PBKDF2.
 */
async function deriveKey(password, salt) {
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    enc.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: PBKDF2_ITERATIONS,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: KEY_LENGTH },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Encrypt a plain string. Returns a base64-encoded string:
 * [salt(16) | iv(12) | ciphertext]
 */
export async function encrypt(plaintext, password) {
  const enc = new TextEncoder();
  const salt = crypto.getRandomValues(new Uint8Array(SALT_LENGTH));
  const iv   = crypto.getRandomValues(new Uint8Array(IV_LENGTH));
  const key  = await deriveKey(password, salt);

  const cipherBuf = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    enc.encode(plaintext)
  );

  // Concatenate salt + iv + ciphertext
  const combined = new Uint8Array(SALT_LENGTH + IV_LENGTH + cipherBuf.byteLength);
  combined.set(salt, 0);
  combined.set(iv, SALT_LENGTH);
  combined.set(new Uint8Array(cipherBuf), SALT_LENGTH + IV_LENGTH);

  return bufToBase64(combined);
}

/**
 * Decrypt a base64-encoded ciphertext. Throws if password is wrong.
 */
export async function decrypt(cipherBase64, password) {
  const combined = base64ToBuf(cipherBase64);
  const salt     = combined.slice(0, SALT_LENGTH);
  const iv       = combined.slice(SALT_LENGTH, SALT_LENGTH + IV_LENGTH);
  const cipher   = combined.slice(SALT_LENGTH + IV_LENGTH);
  const key      = await deriveKey(password, salt);

  const plainBuf = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    key,
    cipher
  );

  return new TextDecoder().decode(plainBuf);
}

/**
 * Hash a password with SHA-256 + random salt for storage comparison.
 * Returns { hash: base64, salt: base64 }
 */
export async function hashPassword(password, saltB64 = null) {
  const enc  = new TextEncoder();
  const salt = saltB64 ? base64ToBuf(saltB64) : crypto.getRandomValues(new Uint8Array(32));
  const data = new Uint8Array([...salt, ...enc.encode(password)]);
  const hashBuf = await crypto.subtle.digest('SHA-256', data);
  return {
    hash: bufToBase64(new Uint8Array(hashBuf)),
    salt: bufToBase64(salt)
  };
}

/**
 * Verify a password against stored hash+salt.
 */
export async function verifyPassword(password, storedHash, storedSalt) {
  const { hash } = await hashPassword(password, storedSalt);
  return hash === storedHash;
}

// ── Utilities ──────────────────────────────────────────────

function bufToBase64(buf) {
  let binary = '';
  const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function base64ToBuf(b64) {
  const binary = atob(b64);
  const bytes  = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}
