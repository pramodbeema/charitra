/**
 * CHARITRA Storage Module
 * All vault data is AES-256-GCM encrypted before being saved to chrome.storage.local.
 * The raw password is NEVER stored. Only a PBKDF2-derived hash + salt is kept
 * to verify login attempts.
 *
 * Storage keys:
 *   hb_config          — { passwordHash, passwordSalt, accent, theme, lockOnClose,
 *                          sessionTimeout, autoUnlock, lockOnBlur, guardEnabled,
 *                          autoSweep, scheduleEnabled, scheduleStart, scheduleEnd,
 *                          welcomeSeen }
 *   hb_blocked_domains — base64 encrypted JSON array of domain strings
 *   hb_vault_entries   — base64 encrypted JSON array of HistoryEntry objects
 *   hb_session         — { expiresAt } (NOT encrypted, just a session token)
 */

import { encrypt, decrypt, hashPassword, verifyPassword } from './crypto.js';

const KEYS = {
  CONFIG:   'hb_config',
  BLOCKED:  'hb_blocked_domains',
  VAULT:    'hb_vault_entries',
  SESSION:  'hb_session',
};

// ── Helpers ──────────────────────────────────────────────────────────────────

function get(keys) {
  return new Promise(resolve => chrome.storage.local.get(keys, resolve));
}

function set(obj) {
  return new Promise(resolve => chrome.storage.local.set(obj, resolve));
}

function remove(keys) {
  return new Promise(resolve => chrome.storage.local.remove(keys, resolve));
}

// ── Password / Auth ──────────────────────────────────────────────────────────

export async function isSetup() {
  const data = await get(KEYS.CONFIG);
  return !!data[KEYS.CONFIG]?.passwordHash;
}

export async function setupPassword(password) {
  const { hash, salt } = await hashPassword(password);
  const existing = (await get(KEYS.CONFIG))[KEYS.CONFIG] || {};
  await set({
    [KEYS.CONFIG]: {
      ...existing,
      passwordHash: hash,
      passwordSalt: salt,
    }
  });
  // Encrypt empty vault with new password
  await saveBlockedDomains([], password);
  await saveVaultEntries([], password);
}

export async function checkPassword(password) {
  const data  = await get(KEYS.CONFIG);
  const cfg   = data[KEYS.CONFIG];
  if (!cfg?.passwordHash) return false;
  return verifyPassword(password, cfg.passwordHash, cfg.passwordSalt);
}

export async function changePassword(oldPassword, newPassword) {
  const valid = await checkPassword(oldPassword);
  if (!valid) throw new Error('Incorrect current password');

  // Re-encrypt all vault data with new password
  const domains = await getBlockedDomains(oldPassword);
  const entries = await getVaultEntries(oldPassword);

  const { hash, salt } = await hashPassword(newPassword);
  const existing = (await get(KEYS.CONFIG))[KEYS.CONFIG] || {};
  await set({
    [KEYS.CONFIG]: { ...existing, passwordHash: hash, passwordSalt: salt }
  });
  await saveBlockedDomains(domains, newPassword);
  await saveVaultEntries(entries, newPassword);
}

// ── Session ───────────────────────────────────────────────────────────────────

export async function createSession(timeoutMinutes = 30) {
  const expiresAt = Date.now() + timeoutMinutes * 60 * 1000;
  await set({ [KEYS.SESSION]: { expiresAt } });
}

export async function getSession() {
  const data = await get(KEYS.SESSION);
  const session = data[KEYS.SESSION];
  if (!session) return null;
  if (Date.now() > session.expiresAt) {
    await clearSession();
    return null;
  }
  return session;
}

export async function refreshSession() {
  const cfg = (await get(KEYS.CONFIG))[KEYS.CONFIG] || {};
  const timeout = cfg.sessionTimeout ?? 30;
  const session = await getSession();
  if (session) {
    await createSession(timeout);
  }
}

export async function clearSession() {
  await remove(KEYS.SESSION);
}

// ── Config ───────────────────────────────────────────────────────────────────

export async function getConfig() {
  const data = await get(KEYS.CONFIG);
  return data[KEYS.CONFIG] || {};
}

export async function saveConfig(cfg) {
  const existing = (await get(KEYS.CONFIG))[KEYS.CONFIG] || {};
  await set({ [KEYS.CONFIG]: { ...existing, ...cfg } });
}

// ── Blocked Domains ──────────────────────────────────────────────────────────

export async function getBlockedDomains(password) {
  const data = await get(KEYS.BLOCKED);
  const enc  = data[KEYS.BLOCKED];
  if (!enc) return [];
  try {
    const json = await decrypt(enc, password);
    return JSON.parse(json);
  } catch {
    throw new Error('Failed to decrypt — wrong password or corrupted data');
  }
}

export async function saveBlockedDomains(domains, password) {
  const json = JSON.stringify(domains);
  const enc  = await encrypt(json, password);
  await set({ [KEYS.BLOCKED]: enc });
}

export async function addBlockedDomain(domain, password) {
  const domains = await getBlockedDomains(password);
  const normalized = normalizeDomain(domain);
  if (!normalized || domains.includes(normalized)) return false;
  domains.push(normalized);
  await saveBlockedDomains(domains, password);
  return true;
}

export async function addBlockedDomains(rawList, password) {
  const domains = await getBlockedDomains(password);
  const added = [];
  for (const raw of rawList) {
    const d = normalizeDomain(raw);
    if (d && !domains.includes(d)) {
      domains.push(d);
      added.push(d);
    }
  }
  await saveBlockedDomains(domains, password);
  return added;
}

export async function removeBlockedDomain(domain, password) {
  const domains = await getBlockedDomains(password);
  const filtered = domains.filter(d => d !== domain);
  await saveBlockedDomains(filtered, password);
}

// ── Vault Entries ────────────────────────────────────────────────────────────

export async function getVaultEntries(password) {
  const data = await get(KEYS.VAULT);
  const enc  = data[KEYS.VAULT];
  if (!enc) return [];
  try {
    const json = await decrypt(enc, password);
    return JSON.parse(json);
  } catch {
    throw new Error('Failed to decrypt vault — wrong password or corrupted data');
  }
}

export async function saveVaultEntries(entries, password) {
  const json = JSON.stringify(entries);
  const enc  = await encrypt(json, password);
  await set({ [KEYS.VAULT]: enc });
}

export async function addVaultEntry(entry, password) {
  const entries = await getVaultEntries(password);
  entries.unshift({ ...entry, id: genId(), savedAt: Date.now() });
  await saveVaultEntries(entries, password);
}

export async function deleteVaultEntry(id, password) {
  const entries = await getVaultEntries(password);
  await saveVaultEntries(entries.filter(e => e.id !== id), password);
}

export async function deleteVaultEntries(ids, password) {
  const entries = await getVaultEntries(password);
  await saveVaultEntries(entries.filter(e => !ids.includes(e.id)), password);
}

export async function clearVault(password) {
  await saveVaultEntries([], password);
}

// ── Utilities ────────────────────────────────────────────────────────────────

export function normalizeDomain(input) {
  if (!input) return null;
  let s = input.trim().toLowerCase();
  // Strip protocol
  s = s.replace(/^https?:\/\//i, '');
  // Strip path/query/hash
  s = s.split('/')[0].split('?')[0].split('#')[0];
  // Strip www.
  if (s.startsWith('www.')) s = s.slice(4);
  // Basic validation
  if (!s || !s.includes('.')) return null;
  return s;
}

function genId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}
