/**
 * CHARITRA Background Service Worker
 * - Intercepts navigation to blocked domains
 * - Deletes matching history entries
 * - Stores them encrypted in vault
 * - Manages session expiry alarms
 */

/**
 * Inline normalizeDomain — background cannot import storage (crypto dependency).
 * The full storage module is used only from popup/vault pages.
 */
function normalizeDomain(input) {
  if (!input) return null;
  let s = input.trim().toLowerCase();
  s = s.replace(/^https?:\/\//i, '');
  s = s.split('/')[0].split('?')[0].split('#')[0];
  if (s.startsWith('www.')) s = s.slice(4);
  if (!s || !s.includes('.')) return null;
  return s;
}

const ALARM_SESSION = 'hb_session_check';
const ALARM_SWEEP   = 'hb_history_sweep';

// ── First install: open welcome page ─────────────────────────────────────────
chrome.runtime.onInstalled.addListener(({ reason }) => {
  if (reason === 'install') {
    chrome.tabs.create({ url: chrome.runtime.getURL('pages/welcome.html') });
  }
});

// ── Alarm: periodic session expiry check ─────────────────────────────────────
chrome.alarms.create(ALARM_SESSION, { periodInMinutes: 1 });
chrome.alarms.create(ALARM_SWEEP,   { periodInMinutes: 2 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === ALARM_SESSION) {
    await checkSessionExpiry();
  } else if (alarm.name === ALARM_SWEEP) {
    await sweepBlockedHistory();
  }
});

// ── webNavigation listener ────────────────────────────────────────────────────
chrome.webNavigation.onCommitted.addListener(async (details) => {
  if (details.frameId !== 0) return; // main frame only
  if (!details.url || details.url.startsWith('chrome://')) return;

  if (!await isGuardActive()) return;

  const domain = normalizeDomain(details.url);
  if (!domain) return;

  const blocked = await getBlockedDomainsRaw();
  if (!blocked.includes(domain)) return;

  // Small delay to let Chrome record the visit first, then wipe it
  setTimeout(() => deleteHistoryForUrl(details.url), 1500);

  // Save to vault via message to any open popup
  const entry = {
    url:    details.url,
    domain: domain,
    title:  '',   // will be updated by content script
    visitedAt: Date.now(),
    tabId: details.tabId,
  };
  await queueVaultEntry(entry);
});

// Also listen for history state changes (SPAs)
chrome.webNavigation.onHistoryStateUpdated.addListener(async (details) => {
  if (details.frameId !== 0) return;
  if (!details.url || details.url.startsWith('chrome://')) return;

  if (!await isGuardActive()) return;

  const domain = normalizeDomain(details.url);
  if (!domain) return;

  const blocked = await getBlockedDomainsRaw();
  if (!blocked.includes(domain)) return;

  setTimeout(() => deleteHistoryForUrl(details.url), 1500);
  await queueVaultEntry({ url: details.url, domain, title: '', visitedAt: Date.now() });
});

// ── Message handling from popup / vault page ──────────────────────────────────
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  handleMessage(msg, sender).then(sendResponse).catch(err => sendResponse({ error: err.message }));
  return true; // keep channel open for async
});

async function handleMessage(msg) {
  switch (msg.type) {
    case 'GET_BLOCKED_RAW':
      return { domains: await getBlockedDomainsRaw() };

    case 'UPDATE_TITLE': {
      // Content script reports page title for a queued entry
      const { url, title } = msg;
      await updateQueuedTitle(url, title);
      return { ok: true };
    }

    case 'SWEEP_NOW':
      await sweepBlockedHistory();
      return { ok: true };

    case 'DELETE_HISTORY_URL':
      await deleteHistoryForUrl(msg.url);
      return { ok: true };

    case 'REFRESH_SESSION':
      await refreshSessionAlarm();
      return { ok: true };

    case 'GET_QUEUED_ENTRIES': {
      const queued = await getQueued();
      return { entries: queued };
    }

    case 'CLEAR_QUEUE':
      await clearQueue();
      return { ok: true };

    case 'CHECK_SCHEDULE': {
      const active = await isGuardActive();
      return { active };
    }

    default:
      return { error: 'Unknown message type' };
  }
}

// ── Schedule check ────────────────────────────────────────────────────────────
async function isGuardActive() {
  const data = await new Promise(r => chrome.storage.local.get('hb_config', r));
  const cfg  = data['hb_config'] || {};
  if (cfg.guardEnabled === false) return false;
  if (!cfg.scheduleEnabled) return true;

  const now   = new Date();
  const hhmm  = now.getHours() * 60 + now.getMinutes();

  const toMinutes = (str) => {
    if (!str) return null;
    const [h, m] = str.split(':').map(Number);
    return h * 60 + m;
  };

  const start = toMinutes(cfg.scheduleStart);
  const end   = toMinutes(cfg.scheduleEnd);
  if (start == null || end == null) return true;

  if (start <= end) {
    return hhmm >= start && hhmm < end;
  } else {
    // Overnight schedule e.g. 22:00 – 06:00
    return hhmm >= start || hhmm < end;
  }
}

// ── History deletion ──────────────────────────────────────────────────────────
async function deleteHistoryForUrl(url) {
  return new Promise(resolve => {
    chrome.history.deleteUrl({ url }, resolve);
  });
}

async function sweepBlockedHistory() {
  const blocked = await getBlockedDomainsRaw();
  if (!blocked.length) return;

  const now       = Date.now();
  const startTime = now - 7 * 24 * 60 * 60 * 1000; // last 7 days

  const items = await new Promise(resolve =>
    chrome.history.search({ text: '', startTime, maxResults: 5000 }, resolve)
  );

  for (const item of items) {
    const domain = normalizeDomain(item.url);
    if (domain && blocked.includes(domain)) {
      await deleteHistoryForUrl(item.url);
    }
  }
}

// ── Blocked domains (raw, unencrypted for background use) ────────────────────
// The background worker stores a plaintext shadow copy of blocked domains
// so it can match without needing the password. This is safe because it
// only contains domain strings, no history content.
const BLOCKED_SHADOW_KEY = 'hb_blocked_shadow';

async function getBlockedDomainsRaw() {
  return new Promise(resolve => {
    chrome.storage.local.get(BLOCKED_SHADOW_KEY, data => {
      resolve(data[BLOCKED_SHADOW_KEY] || []);
    });
  });
}

// ── Vault entry queue ─────────────────────────────────────────────────────────
// Background cannot encrypt (no password). It queues entries.
// Popup reads queue and encrypts them into the vault when unlocked.
const QUEUE_KEY = 'hb_queue';

async function queueVaultEntry(entry) {
  const data  = await new Promise(r => chrome.storage.local.get(QUEUE_KEY, r));
  const queue = data[QUEUE_KEY] || [];
  // Avoid duplicates (same URL within last 5 seconds)
  const isDup = queue.some(e => e.url === entry.url && (entry.visitedAt - e.visitedAt) < 5000);
  if (!isDup) {
    queue.unshift(entry);
    if (queue.length > 500) queue.length = 500; // cap
    await new Promise(r => chrome.storage.local.set({ [QUEUE_KEY]: queue }, r));
  }
}

async function updateQueuedTitle(url, title) {
  const data  = await new Promise(r => chrome.storage.local.get(QUEUE_KEY, r));
  const queue = data[QUEUE_KEY] || [];
  const idx   = queue.findIndex(e => e.url === url);
  if (idx !== -1 && title) {
    queue[idx].title = title;
    await new Promise(r => chrome.storage.local.set({ [QUEUE_KEY]: queue }, r));
  }
}

async function getQueued() {
  const data = await new Promise(r => chrome.storage.local.get(QUEUE_KEY, r));
  return data[QUEUE_KEY] || [];
}

async function clearQueue() {
  await new Promise(r => chrome.storage.local.remove(QUEUE_KEY, r));
}

// ── Session expiry ────────────────────────────────────────────────────────────
async function checkSessionExpiry() {
  const data = await new Promise(r => chrome.storage.local.get('hb_session', r));
  const session = data['hb_session'];
  if (session && Date.now() > session.expiresAt) {
    await new Promise(r => chrome.storage.local.remove('hb_session', r));
  }
}

async function refreshSessionAlarm() {
  // Called by popup to reset session timer
  const data = await new Promise(r => chrome.storage.local.get(['hb_session', 'hb_config'], r));
  const session = data['hb_session'];
  const cfg     = data['hb_config'] || {};
  if (session) {
    const timeout = cfg.sessionTimeout ?? 30;
    await new Promise(r => chrome.storage.local.set({
      hb_session: { expiresAt: Date.now() + timeout * 60 * 1000 }
    }, r));
  }
}
