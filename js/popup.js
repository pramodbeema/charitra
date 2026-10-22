/**
 * CHARITRA Popup Controller — v1.1
 *
 * New in v1.1:
 *  • Auto-unlock on correct password (setting: autoUnlock)
 *  • Dark / Light / System theme picker (first run + settings)
 *  • Lock on window blur (setting: lockOnBlur)
 *  • Scheduled enable/disable with start/end time (setting: scheduleEnabled)
 *  • Advanced vault search: keyword + date range
 */

import {
  isSetup, setupPassword, checkPassword, changePassword,
  createSession, clearSession,
  getConfig, saveConfig,
  getBlockedDomains, saveBlockedDomains,
  addBlockedDomains,
  getVaultEntries, saveVaultEntries,
  deleteVaultEntry, deleteVaultEntries, clearVault,
  normalizeDomain
} from './storage.js';

// ── State ─────────────────────────────────────────────────────────────────────
let SESSION_PASSWORD    = null;
let vaultEntriesCache   = [];
let blockedDomainsCache = [];
let currentEntryId      = null;
let confirmCallback     = null;
let selectedVaultIds    = new Set();
let eventsWereBound     = false;
let autoUnlockEnabled   = false;  // cached from config
let lockOnBlurEnabled   = false;  // cached from config

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  bindAllEvents();

  const cfg = await getConfig();
  applyTheme(cfg.theme || 'dark');
  applyAccent(cfg.accent || 'blue');
  autoUnlockEnabled = cfg.autoUnlock === true;
  lockOnBlurEnabled = cfg.lockOnBlur === true;

  const setup = await isSetup();
  if (!setup) {
    showScreen('setup');
    return;
  }
  showScreen('lock');
});

// ── Visibility / blur lock ────────────────────────────────────────────────────
document.addEventListener('visibilitychange', async () => {
  if (!lockOnBlurEnabled) return;
  if (document.visibilityState === 'hidden' && SESSION_PASSWORD) {
    await doLock();
  }
});

// ── Screen switcher ───────────────────────────────────────────────────────────
function showScreen(name) {
  el('lockScreen').style.display  = name === 'lock'  ? 'flex' : 'none';
  el('setupScreen').style.display = name === 'setup' ? 'flex' : 'none';
  el('mainApp').style.display     = name === 'main'  ? 'flex' : 'none';

  if (name === 'lock')  { el('lockPassword').value = ''; el('lockPassword').focus(); }
  if (name === 'setup') el('setupPw1').focus();
}

// ── Apply theme & accent ──────────────────────────────────────────────────────
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme || 'dark');
}

function applyAccent(accent) {
  if (accent) document.documentElement.setAttribute('data-accent', accent);
  document.querySelectorAll('.color-swatch').forEach(b => {
    b.classList.toggle('active', b.dataset.accent === accent);
  });
}

// ── Bind all events ONCE ──────────────────────────────────────────────────────
function bindAllEvents() {
  if (eventsWereBound) return;
  eventsWereBound = true;

  // Setup screen
  el('setupReveal1').onclick   = () => toggleReveal('setupPw1', 'setupReveal1');
  el('setupCreate').onclick    = doSetup;
  el('setupPw1').onkeydown     = e => { if (e.key === 'Enter') el('setupPw2').focus(); };
  el('setupPw2').onkeydown     = e => { if (e.key === 'Enter') doSetup(); };
  el('themePickerDark').onclick   = () => pickTheme('dark');
  el('themePickerLight').onclick  = () => pickTheme('light');
  el('themePickerSystem').onclick = () => pickTheme('system');

  // Lock screen — auto-unlock on input
  el('lockReveal').onclick     = () => toggleReveal('lockPassword', 'lockReveal');
  el('lockUnlock').onclick     = doUnlock;
  el('lockForgot').onclick     = doForgotPassword;
  el('lockPassword').onkeydown = e => { if (e.key === 'Enter') doUnlock(); };
  el('lockPassword').oninput   = debounce(tryAutoUnlock, 400);

  // Top bar — lock + vault open
  el('btnLock').onclick        = doLock;
  el('btnOpenVault').onclick   = () => chrome.tabs.create({ url: chrome.runtime.getURL('pages/vault.html') });
  // Guard pill toggles protection on/off
  el('guardStatus').onclick    = doToggleGuard;

  // Pivot
  el('pivotHeader').addEventListener('click', e => {
    const tab = e.target.closest('[data-tab]');
    if (tab) switchTab(tab.dataset.tab);
  });

  // Dashboard
  el('btnQuickAdd').onclick   = doQuickAdd;
  el('quickDomain').onkeydown = e => { if (e.key === 'Enter') doQuickAdd(); };
  el('tile-blocked').onclick  = () => switchTab('domains');
  el('tile-vault').onclick    = () => switchTab('vault');
  // Current tab banner — single block button drives all checked actions
  el('btnBlockCurrent').onclick  = doBlockCurrentTabWithOptions;

  // Domains tab
  el('btnAddDomain').onclick     = doAddDomain;
  el('addDomainInput').onkeydown = e => { if (e.key === 'Enter') doAddDomain(); };
  el('btnBulkAdd').onclick       = () => openDialog('bulkDialog');
  el('btnClearDomains').onclick  = () => doConfirm(
    'clear all blocked domains?',
    'This will unblock all domains. Vault entries are not affected.',
    async () => {
      blockedDomainsCache = [];
      await saveBlockedDomains([], SESSION_PASSWORD);
      await syncShadow([]);
      renderDomainList();
      updateDashboard();
      snack('All domains cleared');
    }
  );
  el('domainSearch').oninput = renderDomainList;

  // Vault tab
  el('vaultSearch').oninput        = () => renderVaultList();
  el('vaultDateFrom').onchange     = () => renderVaultList();
  el('vaultDateTo').onchange       = () => renderVaultList();
  el('btnClearVaultSearch').onclick = clearVaultSearch;
  el('selectAllVault').onchange    = onSelectAllVault;
  el('btnDeleteSelected').onclick  = doDeleteSelected;
  el('btnClearVault').onclick      = () => doConfirm(
    'clear entire vault?',
    'All private history entries will be permanently deleted.',
    async () => {
      await clearVault(SESSION_PASSWORD);
      vaultEntriesCache = [];
      selectedVaultIds.clear();
      renderVaultList();
      renderRecentList();
      updateDashboard();
      snack('Vault cleared');
    }
  );
  el('btnExportVault').onclick = () => {
    el('exportPassword').value    = '';
    el('exportError').textContent = '';
    openDialog('exportDialog');
  };

  // Settings — no guardToggle (controlled by topbar pill)
  el('lockOnCloseToggle').onchange   = saveSettings;
  el('autoSweepToggle').onchange     = saveSettings;
  el('autoUnlockToggle').onchange    = saveSettings;
  el('lockOnBlurToggle').onchange    = saveSettings;
  el('scheduleToggle').onchange      = saveSettings;
  el('sessionTimeoutInput').onchange = saveSettings;
  el('scheduleStart').onchange       = saveSettings;
  el('scheduleEnd').onchange         = saveSettings;
  el('btnChangePassword').onclick    = doChangePassword;
  el('btnSweepNow').onclick          = doSweepNow;
  el('btnOpenWelcome').onclick       = () => chrome.tabs.create({ url: chrome.runtime.getURL('pages/welcome.html') });
  el('btnResetAll').onclick          = () => doConfirm(
    'reset everything?',
    'ALL vault data, blocked domains, and your password will be permanently deleted.',
    doResetAll
  );
  document.querySelectorAll('.color-swatch').forEach(btn => {
    btn.onclick = () => setAccent(btn.dataset.accent);
  });
  document.querySelectorAll('.theme-tile').forEach(tile => {
    tile.onclick = () => setTheme(tile.dataset.theme);
  });

  // Bulk dialog
  el('bulkCancel').onclick   = () => closeDialog('bulkDialog');
  el('bulkConfirm').onclick  = doBulkAdd;
  el('bulkTextarea').oninput = updateBulkPreview;

  // Entry dialog
  el('entryDialogDelete').onclick = doDeleteCurrentEntry;
  el('entryDialogClose').onclick  = () => closeDialog('entryDialog');

  // Confirm dialog
  el('confirmNo').onclick  = () => closeDialog('confirmDialog');
  el('confirmYes').onclick = async () => {
    closeDialog('confirmDialog');
    if (confirmCallback) { await confirmCallback(); confirmCallback = null; }
  };

  // Export dialog
  el('exportCancel').onclick  = () => closeDialog('exportDialog');
  el('exportConfirm').onclick = doExport;

  // Overlay-click to close
  ['bulkDialog','entryDialog','confirmDialog','exportDialog'].forEach(id => {
    el(id).addEventListener('click', e => { if (e.target === el(id)) closeDialog(id); });
  });
}

// ── Dialog helpers ────────────────────────────────────────────────────────────
function openDialog(id)  { el(id).style.display = 'flex'; }
function closeDialog(id) { el(id).style.display = 'none'; }

// ── Theme picker (setup screen) ───────────────────────────────────────────────
let pendingTheme = 'dark';
function pickTheme(theme) {
  pendingTheme = theme;
  document.querySelectorAll('.theme-pick-tile').forEach(t => {
    t.classList.toggle('active', t.dataset.theme === theme);
  });
  applyTheme(theme);
}

// ── Setup ─────────────────────────────────────────────────────────────────────
async function doSetup() {
  const pw1 = el('setupPw1').value;
  const pw2 = el('setupPw2').value;
  if (pw1.length < 6) return setError('setupError', 'password must be at least 6 characters');
  if (pw1 !== pw2)    return setError('setupError', 'passwords do not match');

  el('setupProgress').style.display = 'block';
  el('setupCreate').disabled = true;
  clearError('setupError');

  try {
    await setupPassword(pw1);
    await saveConfig({ theme: pendingTheme, welcomeSeen: true });
    SESSION_PASSWORD = pw1;
    await createSession(30);
    applyTheme(pendingTheme);
    showScreen('main');
    await refreshAll();
    loadCurrentTab();
  } catch (err) {
    setError('setupError', err.message);
  } finally {
    el('setupProgress').style.display = 'none';
    el('setupCreate').disabled = false;
  }
}

// ── Auto-unlock (fires on password input) ─────────────────────────────────────
async function tryAutoUnlock() {
  if (!autoUnlockEnabled) return;
  const pw = el('lockPassword').value.trim();
  if (pw.length < 6) return;
  const ok = await checkPassword(pw).catch(() => false);
  if (ok) {
    SESSION_PASSWORD = pw;
    await createSession(30);
    showScreen('main');
    await refreshAll();
    await flushQueue();
    loadCurrentTab();
  }
}

// ── Unlock ────────────────────────────────────────────────────────────────────
async function doUnlock() {
  const pw = el('lockPassword').value.trim();
  if (!pw) return setError('lockError', 'enter your password');

  el('lockUnlock').disabled    = true;
  el('lockUnlock').textContent = 'unlocking…';
  clearError('lockError');

  try {
    const ok = await checkPassword(pw);
    if (!ok) {
      setError('lockError', 'incorrect password');
      el('lockPassword').value = '';
      el('lockPassword').focus();
      return;
    }
    SESSION_PASSWORD = pw;
    await createSession(30);
    showScreen('main');
    await refreshAll();
    await flushQueue();
    loadCurrentTab();
  } catch (err) {
    setError('lockError', err.message);
  } finally {
    el('lockUnlock').disabled    = false;
    el('lockUnlock').textContent = 'unlock';
  }
}

// ── Lock ──────────────────────────────────────────────────────────────────────
async function doLock() {
  SESSION_PASSWORD = null;
  await clearSession();
  clearError('lockError');
  showScreen('lock');
}

async function doForgotPassword() {
  doConfirm(
    'reset vault?',
    'ALL vault data, blocked domains, and your password will be permanently deleted.',
    async () => {
      await chrome.storage.local.clear();
      SESSION_PASSWORD = null;
      el('setupPw1').value = ''; el('setupPw2').value = '';
      clearError('setupError');
      showScreen('setup');
      snack('Vault reset — set a new password');
    }
  );
}

// ── Queue flush ───────────────────────────────────────────────────────────────
async function flushQueue() {
  let resp;
  try { resp = await chrome.runtime.sendMessage({ type: 'GET_QUEUED_ENTRIES' }); } catch { return; }

  const queue = resp?.entries || [];
  if (!queue.length) return;

  const existingKeys = new Set(vaultEntriesCache.map(e => e.url + ':' + e.visitedAt));
  let added = 0;
  for (const entry of queue) {
    const key = entry.url + ':' + entry.visitedAt;
    if (!existingKeys.has(key)) {
      vaultEntriesCache.unshift({ ...entry, id: genId(), savedAt: Date.now() });
      existingKeys.add(key);
      added++;
    }
  }
  if (added > 0) {
    await saveVaultEntries(vaultEntriesCache, SESSION_PASSWORD);
    snack(`${added} new entr${added > 1 ? 'ies' : 'y'} captured`);
  }
  try { await chrome.runtime.sendMessage({ type: 'CLEAR_QUEUE' }); } catch {}

  renderVaultList();
  renderRecentList();
  updateDashboard();
}

// ── Refresh ───────────────────────────────────────────────────────────────────
async function refreshAll() {
  await Promise.all([refreshDomains(), refreshVault(), loadSettings()]);
  updateDashboard();
}

async function refreshDomains() {
  try {
    blockedDomainsCache = await getBlockedDomains(SESSION_PASSWORD);
    await syncShadow(blockedDomainsCache);
    renderDomainList();
  } catch { /* handled at unlock */ }
}

async function refreshVault() {
  try {
    vaultEntriesCache = await getVaultEntries(SESSION_PASSWORD);
    renderVaultList();
    renderRecentList();
  } catch { /* handled */ }
}

// ── Domain management ─────────────────────────────────────────────────────────
async function doQuickAdd() {
  const domain = normalizeDomain(el('quickDomain').value.trim());
  if (!domain) { el('quickAddFeedback').textContent = 'invalid domain'; return; }
  if (blockedDomainsCache.includes(domain)) {
    el('quickAddFeedback').textContent = `${domain} already blocked`;
    setTimeout(() => { el('quickAddFeedback').textContent = ''; }, 3000);
    return;
  }
  blockedDomainsCache.push(domain);
  await saveBlockedDomains(blockedDomainsCache, SESSION_PASSWORD);
  await syncShadow(blockedDomainsCache);
  el('quickDomain').value = '';
  el('quickAddFeedback').textContent = `✓ ${domain} blocked`;
  renderDomainList(); updateDashboard();
  setTimeout(() => { el('quickAddFeedback').textContent = ''; }, 3000);
}

async function doAddDomain() {
  const domain = normalizeDomain(el('addDomainInput').value.trim());
  if (!domain)                              return snack('Invalid domain', true);
  if (blockedDomainsCache.includes(domain)) return snack(`${domain} already blocked`, true);
  blockedDomainsCache.push(domain);
  await saveBlockedDomains(blockedDomainsCache, SESSION_PASSWORD);
  await syncShadow(blockedDomainsCache);
  el('addDomainInput').value = '';
  renderDomainList(); updateDashboard();
  snack(`${domain} blocked`);
}

async function doRemoveDomain(domain) {
  blockedDomainsCache = blockedDomainsCache.filter(d => d !== domain);
  await saveBlockedDomains(blockedDomainsCache, SESSION_PASSWORD);
  await syncShadow(blockedDomainsCache);
  renderDomainList(); updateDashboard();
  snack(`${domain} unblocked`);
}

function updateBulkPreview() {
  const n = el('bulkTextarea').value.split('\n').filter(l => normalizeDomain(l)).length;
  el('bulkPreviewCount').textContent = `${n} valid domain${n !== 1 ? 's' : ''} found`;
}

async function doBulkAdd() {
  const lines = el('bulkTextarea').value.split('\n').map(l => l.trim()).filter(Boolean);
  const added = await addBlockedDomains(lines, SESSION_PASSWORD);
  blockedDomainsCache = await getBlockedDomains(SESSION_PASSWORD);
  await syncShadow(blockedDomainsCache);
  closeDialog('bulkDialog');
  el('bulkTextarea').value = '';
  renderDomainList(); updateDashboard();
  snack(`${added.length} domain${added.length !== 1 ? 's' : ''} added`);
}

function renderDomainList() {
  const query    = (el('domainSearch').value || '').toLowerCase();
  const filtered = blockedDomainsCache.filter(d => d.includes(query));
  el('domainListCount').textContent = `${filtered.length} domain${filtered.length !== 1 ? 's' : ''}`;
  const list = el('domainList');
  if (!filtered.length) {
    list.innerHTML = `<div class="metro-empty" style="padding:16px;">
      <div class="metro-empty-icon" style="font-size:24px;">🛡</div>
      <div class="metro-empty-text" style="font-size:12px;">${query ? 'no match' : 'no blocked domains yet'}</div>
    </div>`;
    return;
  }
  list.innerHTML = filtered.map(d => `
    <div class="domain-item">
      <div class="domain-favicon">${d[0].toUpperCase()}</div>
      <span class="domain-name" title="${esc(d)}">${esc(d)}</span>
      <button class="domain-del" data-domain="${esc(d)}" title="Unblock">✕</button>
    </div>`).join('');
  list.querySelectorAll('.domain-del').forEach(btn => {
    btn.onclick = () => doRemoveDomain(btn.dataset.domain);
  });
}

// ── Vault ─────────────────────────────────────────────────────────────────────
function getVaultFilters() {
  const keyword = (el('vaultSearch').value || '').toLowerCase().trim();
  const fromRaw = el('vaultDateFrom').value;
  const toRaw   = el('vaultDateTo').value;
  const from    = fromRaw ? new Date(fromRaw).getTime() : null;
  const to      = toRaw   ? new Date(toRaw + 'T23:59:59').getTime() : null;
  return { keyword, from, to };
}

function renderVaultList() {
  const { keyword, from, to } = getVaultFilters();
  const hasFilter = keyword || from || to;

  const filtered = vaultEntriesCache.filter(e => {
    if (from && e.visitedAt < from) return false;
    if (to   && e.visitedAt > to)   return false;
    if (keyword) {
      const hay = ((e.title||'') + ' ' + (e.url||'') + ' ' + (e.domain||'')).toLowerCase();
      if (!hay.includes(keyword)) return false;
    }
    return true;
  });

  el('vaultEntryCount').textContent = `${filtered.length} entr${filtered.length !== 1 ? 'ies' : 'y'}`;
  el('btnClearVaultSearch').style.display = hasFilter ? 'inline-flex' : 'none';

  const list = el('vaultList');
  if (!filtered.length) {
    selectedVaultIds.clear(); updateDeleteButton();
    list.innerHTML = `<div class="metro-empty" style="padding:16px;">
      <div class="metro-empty-icon" style="font-size:24px;">🔒</div>
      <div class="metro-empty-text" style="font-size:12px;">${hasFilter ? 'no results' : 'vault is empty'}</div>
    </div>`;
    return;
  }

  list.innerHTML = filtered.map(e => `
    <div class="vault-item" data-id="${esc(e.id)}">
      <div class="vault-item-checkbox">
        <input type="checkbox" class="vault-item-cb" data-id="${esc(e.id)}"
               ${selectedVaultIds.has(e.id) ? 'checked' : ''} />
        <div style="flex:1;min-width:0;">
          <div class="vault-item-title">${esc(e.title || e.url || e.domain)}</div>
          <div class="vault-item-meta">
            <span class="text-accent">${esc(e.domain)}</span>
            <span>${formatTime(e.visitedAt)}</span>
          </div>
        </div>
      </div>
    </div>`).join('');

  list.querySelectorAll('.vault-item-cb').forEach(cb => {
    cb.addEventListener('change', ev => {
      ev.stopPropagation();
      cb.checked ? selectedVaultIds.add(cb.dataset.id) : selectedVaultIds.delete(cb.dataset.id);
      updateDeleteButton(); updateSelectAllCheckbox(filtered);
    });
  });
  list.querySelectorAll('.vault-item').forEach(item => {
    item.addEventListener('click', e => {
      if (e.target.type === 'checkbox') return;
      openEntryDialog(item.dataset.id);
    });
  });
  updateSelectAllCheckbox(filtered); updateDeleteButton();
}

function clearVaultSearch() {
  el('vaultSearch').value   = '';
  el('vaultDateFrom').value = '';
  el('vaultDateTo').value   = '';
  renderVaultList();
}

function renderRecentList() {
  const recent = vaultEntriesCache.slice(0, 5);
  const list   = el('recentList');
  if (!recent.length) {
    list.innerHTML = `<div class="metro-empty" style="padding:12px;">
      <div class="metro-empty-icon" style="font-size:20px;">📂</div>
      <div class="metro-empty-text" style="font-size:12px;">vault is empty</div>
    </div>`;
    return;
  }
  list.innerHTML = recent.map(e => `
    <div class="vault-item" data-id="${esc(e.id)}" style="padding:5px 0;cursor:pointer;">
      <div class="vault-item-title" style="font-size:11px;">${esc(e.title || e.url || e.domain)}</div>
      <div class="vault-item-meta"><span class="text-accent">${esc(e.domain)}</span><span>${formatTime(e.visitedAt)}</span></div>
    </div>`).join('');
  list.querySelectorAll('.vault-item').forEach(item => {
    item.onclick = () => openEntryDialog(item.dataset.id);
  });
}

function openEntryDialog(id) {
  const entry = vaultEntriesCache.find(e => e.id === id);
  if (!entry) return;
  currentEntryId = id;
  el('entryDialogTitle').textContent  = entry.title || entry.domain;
  el('entryDialogDomain').textContent = entry.domain;
  el('entryDialogUrl').textContent    = entry.url;
  el('entryDialogTime').textContent   = formatFull(entry.visitedAt);
  openDialog('entryDialog');
}

async function doDeleteCurrentEntry() {
  if (!currentEntryId) return;
  await deleteVaultEntry(currentEntryId, SESSION_PASSWORD);
  vaultEntriesCache = vaultEntriesCache.filter(e => e.id !== currentEntryId);
  selectedVaultIds.delete(currentEntryId);
  closeDialog('entryDialog');
  renderVaultList(); renderRecentList(); updateDashboard();
  snack('Entry deleted');
}

function onSelectAllVault() {
  const { keyword, from, to } = getVaultFilters();
  const filtered = vaultEntriesCache.filter(e => {
    if (from && e.visitedAt < from) return false;
    if (to   && e.visitedAt > to)   return false;
    if (keyword) {
      const hay = ((e.title||'')+' '+(e.url||'')+' '+(e.domain||'')).toLowerCase();
      if (!hay.includes(keyword)) return false;
    }
    return true;
  });
  const checked = el('selectAllVault').checked;
  filtered.forEach(e => checked ? selectedVaultIds.add(e.id) : selectedVaultIds.delete(e.id));
  renderVaultList();
}

function updateSelectAllCheckbox(filtered) {
  const cb = el('selectAllVault');
  if (!filtered.length) { cb.checked = false; cb.indeterminate = false; return; }
  const n = filtered.filter(e => selectedVaultIds.has(e.id)).length;
  if      (n === 0)               { cb.checked = false; cb.indeterminate = false; }
  else if (n === filtered.length) { cb.checked = true;  cb.indeterminate = false; }
  else                            { cb.indeterminate = true; }
}

function updateDeleteButton() {
  const btn = el('btnDeleteSelected');
  btn.disabled    = selectedVaultIds.size === 0;
  btn.textContent = selectedVaultIds.size > 0 ? `delete (${selectedVaultIds.size})` : 'delete selected';
}

async function doDeleteSelected() {
  if (!selectedVaultIds.size) return;
  const ids = [...selectedVaultIds];
  await deleteVaultEntries(ids, SESSION_PASSWORD);
  vaultEntriesCache = vaultEntriesCache.filter(e => !ids.includes(e.id));
  selectedVaultIds.clear();
  renderVaultList(); renderRecentList(); updateDashboard();
  snack(`${ids.length} entr${ids.length !== 1 ? 'ies' : 'y'} deleted`);
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
function updateDashboard() {
  el('tileBlockedCount').textContent = blockedDomainsCache.length;
  el('tileVaultCount').textContent   = vaultEntriesCache.length;
  const todayStart = new Date(); todayStart.setHours(0,0,0,0);
  el('tileTodayCount').textContent   = vaultEntriesCache.filter(e => e.visitedAt >= todayStart.getTime()).length;
}

// ── Current tab banner ────────────────────────────────────────────────────────
let currentTabDomain = null;

async function loadCurrentTab() {
  try {
    // lastFocusedWindow:true finds the browser window behind the popup,
    // NOT the popup window itself (which has no tabs).
    const tabs = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    const tab  = tabs.find(t => t.url && !t.url.startsWith('chrome://') && !t.url.startsWith('chrome-extension://'));
    if (!tab?.url) return;
    const domain = normalizeDomain(tab.url);
    if (!domain) return; // new tab, about:blank, etc.

    currentTabDomain = domain;

    // If already blocked, hide the banner entirely — nothing to offer
    if (blockedDomainsCache.includes(domain)) {
      el('currentTabBanner').style.display = 'none';
      return;
    }

    el('currentTabDomain').textContent      = domain;
    el('currentTabBanner').style.display    = 'block';
    el('currentTabBlocked').style.display   = 'none';
    el('btnBlockCurrent').textContent       = '+ block this domain';
    el('btnBlockCurrent').disabled          = false;

    // Reset checkboxes and progress each time banner loads
    el('chkImportCurrent').checked          = false;
    el('chkCleanupCurrent').checked         = false;
    el('currentTabProgress').style.display  = 'none';
    el('currentTabProgress').textContent    = '';
  } catch (err) {
    // Silently ignore — can happen if called outside a normal tab context
    console.debug('CHARITRA loadCurrentTab:', err.message);
  }
}

// Single button — runs block + (optionally) import then cleanup in sequence
async function doBlockCurrentTabWithOptions() {
  if (!currentTabDomain) return;

  const doImport  = el('chkImportCurrent').checked;
  const doCleanup = el('chkCleanupCurrent').checked;

  const btn      = el('btnBlockCurrent');
  const progress = el('currentTabProgress');

  btn.disabled = true;
  progress.style.display = 'block';

  try {
    // Step 1 — Block the domain (always)
    if (!blockedDomainsCache.includes(currentTabDomain)) {
      progress.textContent = 'Blocking domain…';
      blockedDomainsCache.push(currentTabDomain);
      await saveBlockedDomains(blockedDomainsCache, SESSION_PASSWORD);
      await syncShadow(blockedDomainsCache);
      renderDomainList();
      updateDashboard();
    }

    // Step 2 — Import history FIRST (before cleanup, so data isn't lost)
    if (doImport) {
      progress.textContent = 'Importing history into vault…';
      const startTime = Date.now() - 90 * 24 * 60 * 60 * 1000;
      const items = await new Promise(resolve =>
        chrome.history.search({ text: currentTabDomain, startTime, maxResults: 500 }, resolve)
      );
      const matches = items.filter(item => normalizeDomain(item.url) === currentTabDomain);
      const existingUrls = new Set(vaultEntriesCache.map(e => e.url));
      let added = 0;
      for (const item of matches) {
        if (!existingUrls.has(item.url)) {
          vaultEntriesCache.unshift({
            id: genId(), url: item.url, domain: currentTabDomain,
            title: item.title || item.url,
            visitedAt: item.lastVisitTime || Date.now(),
            savedAt: Date.now(), imported: true
          });
          existingUrls.add(item.url);
          added++;
        }
      }
      if (added > 0) {
        await saveVaultEntries(vaultEntriesCache, SESSION_PASSWORD);
        renderVaultList();
        renderRecentList();
        updateDashboard();
      }
      progress.textContent = `✓ ${added} entr${added !== 1 ? 'ies' : 'y'} imported`;
      await sleep(600);
    }

    // Step 3 — Cleanup AFTER import (safe ordering)
    if (doCleanup) {
      progress.textContent = 'Cleaning browser history…';
      const startTime = Date.now() - 365 * 24 * 60 * 60 * 1000;
      const items = await new Promise(resolve =>
        chrome.history.search({ text: currentTabDomain, startTime, maxResults: 2000 }, resolve)
      );
      const matches = items.filter(item => normalizeDomain(item.url) === currentTabDomain);
      for (const item of matches) {
        await new Promise(resolve => chrome.history.deleteUrl({ url: item.url }, resolve));
      }
      progress.textContent = `✓ ${matches.length} history entr${matches.length !== 1 ? 'ies' : 'y'} removed`;
      await sleep(600);
    }

    // Done
    const parts = ['Domain blocked'];
    if (doImport)  parts.push('history imported');
    if (doCleanup) parts.push('browser history cleaned');
    progress.textContent = '✓ ' + parts.join(' · ');

    snack(parts.join(', '));

    // Hide the banner — domain is now blocked, no point showing it again
    await sleep(800);
    el('currentTabBanner').style.display = 'none';
  } catch (err) {
    progress.textContent = `Error: ${err.message}`;
    snack(err.message, true);
    btn.disabled = false;
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Settings ──────────────────────────────────────────────────────────────────
async function loadSettings() {
  const cfg = await getConfig();
  el('lockOnCloseToggle').checked  = cfg.lockOnClose    !== false;
  el('autoSweepToggle').checked    = cfg.autoSweep      !== false;
  el('autoUnlockToggle').checked   = cfg.autoUnlock     === true;
  el('lockOnBlurToggle').checked   = cfg.lockOnBlur     === true;
  el('scheduleToggle').checked     = cfg.scheduleEnabled === true;
  el('sessionTimeoutInput').value  = cfg.sessionTimeout ?? 30;
  el('scheduleStart').value        = cfg.scheduleStart  || '09:00';
  el('scheduleEnd').value          = cfg.scheduleEnd    || '17:00';

  updateGuardStatus(cfg.guardEnabled !== false);
  applyTheme(cfg.theme || 'dark');
  applyAccent(cfg.accent || 'blue');

  // Sync runtime state
  autoUnlockEnabled = cfg.autoUnlock === true;
  lockOnBlurEnabled = cfg.lockOnBlur === true;

  // Highlight active theme tile in settings
  document.querySelectorAll('.theme-tile').forEach(t => {
    t.classList.toggle('active', t.dataset.theme === (cfg.theme || 'dark'));
  });

  // Show/hide schedule rows
  toggleScheduleRows(cfg.scheduleEnabled === true);
}

async function saveSettings() {
  const lockOnClose     = el('lockOnCloseToggle').checked;
  const autoSweep       = el('autoSweepToggle').checked;
  const autoUnlock      = el('autoUnlockToggle').checked;
  const lockOnBlur      = el('lockOnBlurToggle').checked;
  const scheduleEnabled = el('scheduleToggle').checked;
  const sessionTimeout  = parseInt(el('sessionTimeoutInput').value, 10) || 30;
  const scheduleStart   = el('scheduleStart').value;
  const scheduleEnd     = el('scheduleEnd').value;

  await saveConfig({ lockOnClose, autoSweep, autoUnlock, lockOnBlur,
                     scheduleEnabled, sessionTimeout, scheduleStart, scheduleEnd });

  autoUnlockEnabled = autoUnlock;
  lockOnBlurEnabled = lockOnBlur;
  toggleScheduleRows(scheduleEnabled);
  snack('Settings saved');
}

// Toggle guard directly from topbar pill
async function doToggleGuard() {
  const cfg       = await getConfig();
  const newState  = !(cfg.guardEnabled !== false);   // flip
  await saveConfig({ guardEnabled: newState });
  updateGuardStatus(newState);
  snack(`Protection ${newState ? 'enabled' : 'disabled'}`);
}

function updateGuardStatus(on) {
  el('guardStatus').textContent = on ? 'ON' : 'OFF';
  el('guardStatus').className   = `status-pill${on ? '' : ' off'}`;
}

function toggleScheduleRows(show) {
  el('scheduleRows').style.display = show ? 'block' : 'none';
}

async function setTheme(theme) {
  applyTheme(theme);
  await saveConfig({ theme });
  document.querySelectorAll('.theme-tile').forEach(t => t.classList.toggle('active', t.dataset.theme === theme));
  snack(`Theme: ${theme}`);
}

async function doChangePassword() {
  const cur  = el('chgPwCurrent').value;
  const nw   = el('chgPwNew').value;
  const conf = el('chgPwConfirm').value;
  if (!cur||!nw||!conf)  return snack('Fill all password fields', true);
  if (nw.length < 6)     return snack('New password must be at least 6 characters', true);
  if (nw !== conf)       return snack('Passwords do not match', true);
  try {
    await changePassword(cur, nw);
    SESSION_PASSWORD = nw;
    el('chgPwCurrent').value = el('chgPwNew').value = el('chgPwConfirm').value = '';
    snack('Password changed successfully');
  } catch (err) { snack(err.message, true); }
}

async function doSweepNow() {
  try { await chrome.runtime.sendMessage({ type: 'SWEEP_NOW' }); } catch {}
  snack('History sweep complete');
}

async function doResetAll() {
  await chrome.storage.local.clear();
  SESSION_PASSWORD = null; blockedDomainsCache = []; vaultEntriesCache = [];
  el('setupPw1').value = el('setupPw2').value = '';
  clearError('setupError');
  showScreen('setup');
  snack('Everything reset');
}

// ── Export ────────────────────────────────────────────────────────────────────
async function doExport() {
  const pw = el('exportPassword').value;
  const ok = await checkPassword(pw);
  if (!ok) { el('exportError').textContent = 'incorrect password'; return; }
  const payload = { exportedAt: new Date().toISOString(), blockedDomains: blockedDomainsCache, vaultEntries: vaultEntriesCache };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), { href: url, download: `CHARITRA-export-${Date.now()}.json` });
  a.click(); URL.revokeObjectURL(url);
  closeDialog('exportDialog');
  snack('Exported successfully');
}

// ── Accent / theme helpers ────────────────────────────────────────────────────
async function setAccent(accent) {
  applyAccent(accent);
  await saveConfig({ accent });
  snack(`Accent: ${accent}`);
}

async function syncShadow(domains) {
  await chrome.storage.local.set({ hb_blocked_shadow: domains });
}

// ── Pivot tabs ────────────────────────────────────────────────────────────────
function switchTab(tabId) {
  document.querySelectorAll('.metro-pivot-tab').forEach(t =>
    t.classList.toggle('active', t.dataset.tab === tabId));
  document.querySelectorAll('.metro-pivot-panel').forEach(p =>
    p.classList.toggle('active', p.id === `tab-${tabId}`));
  if (tabId === 'vault')   renderVaultList();
  if (tabId === 'domains') renderDomainList();
}

// ── Confirm helper ────────────────────────────────────────────────────────────
function doConfirm(title, body, cb) {
  el('confirmTitle').textContent = title;
  el('confirmBody').textContent  = body;
  confirmCallback = cb;
  openDialog('confirmDialog');
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function el(id) { return document.getElementById(id); }
function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function toggleReveal(inputId, btnId) {
  const inp = el(inputId);
  inp.type = inp.type === 'password' ? 'text' : 'password';
  el(btnId).textContent = inp.type === 'password' ? '👁' : '🙈';
}
function setError(id, msg)  { el(id).textContent = msg; }
function clearError(id)     { el(id).textContent = ''; }

let snackTimer;
function snack(msg, isError = false) {
  const s = el('snack');
  s.textContent = msg;
  s.className   = `show${isError ? ' error' : ''}`;
  clearTimeout(snackTimer);
  snackTimer = setTimeout(() => { s.className = ''; }, 3000);
}
function formatTime(ts) {
  if (!ts) return '';
  const d = Date.now() - ts;
  if (d < 60000)    return 'just now';
  if (d < 3600000)  return `${Math.floor(d/60000)}m ago`;
  if (d < 86400000) return `${Math.floor(d/3600000)}h ago`;
  return new Date(ts).toLocaleDateString();
}
function formatFull(ts) { return ts ? new Date(ts).toLocaleString() : ''; }
function genId() { return Date.now().toString(36) + Math.random().toString(36).slice(2,7); }
function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}
