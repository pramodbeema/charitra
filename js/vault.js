/**
 * CHARITRA Vault Page Controller
 * Full-page vault with table view, analytics, domain management.
 */

import {
  isSetup, checkPassword, createSession, getSession, clearSession,
  getConfig, saveConfig,
  getBlockedDomains, saveBlockedDomains, addBlockedDomains, removeBlockedDomain,
  getVaultEntries, saveVaultEntries, deleteVaultEntries, clearVault,
  normalizeDomain
} from './storage.js';

// ── State ─────────────────────────────────────────────────────────────────────
let PASSWORD = null;
let vault    = [];
let domains  = [];
let filtered = [];
let sortCol  = 'visitedAt';
let sortDir  = 'desc';
let page     = 1;
const PAGE_SIZE = 50;
let activeFilter = 'all';
let searchQuery  = '';
let selectedIds  = new Set();
let vaultConfirmCallback = null;

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  if (!await isSetup()) {
    el('vaultLock').innerHTML = `<div style="font-size:32px;">🛡</div><div style="font-size:20px;font-weight:300;">no vault found</div><div style="font-size:13px;color:var(--fg-secondary);">Open the extension popup to set up your vault.</div>`;
    return;
  }
  await applyAccentFromConfig();
  bindLockEvents();
});

async function applyAccentFromConfig() {
  const cfg = await getConfig();
  if (cfg.accent) document.documentElement.setAttribute('data-accent', cfg.accent);
  if (cfg.theme)  document.documentElement.setAttribute('data-theme',  cfg.theme);
  return cfg;
}

// ── Lock ──────────────────────────────────────────────────────────────────────
function bindLockEvents() {
  el('vaultReveal').onclick = () => toggleReveal('vaultPw', 'vaultReveal');
  el('vaultUnlock').onclick = doUnlock;
  el('vaultPw').onkeydown   = e => { if (e.key === 'Enter') doUnlock(); };
  // Auto-unlock on input (respects the autoUnlock setting)
  el('vaultPw').oninput     = debounce(tryVaultAutoUnlock, 400);
}

async function tryVaultAutoUnlock() {
  const cfg = await getConfig();
  if (!cfg.autoUnlock) return;
  const pw = el('vaultPw').value.trim();
  if (pw.length < 6) return;
  const ok = await checkPassword(pw).catch(() => false);
  if (ok) {
    PASSWORD = pw;
    await createSession(cfg.sessionTimeout || 30);
    hide('vaultLock');
    show('vaultMain');
    bindMainEvents();
    await refreshAll();
    await flushQueue();
  }
}

async function doUnlock() {
  const pw = el('vaultPw').value;
  if (!pw) return;
  el('vaultUnlock').disabled = true;
  el('vaultUnlock').textContent = 'unlocking…';

  try {
    const ok = await checkPassword(pw);
    if (!ok) {
      el('vaultLockError').textContent = 'incorrect password';
      el('vaultPw').value = '';
      el('vaultPw').focus();
      return;
    }
    PASSWORD = pw;
    const cfg = await getConfig();
    await createSession(cfg.sessionTimeout || 30);
    hide('vaultLock');
    show('vaultMain');
    bindMainEvents();
    await refreshAll();
    await flushQueue();
  } catch (e) {
    el('vaultLockError').textContent = e.message;
  } finally {
    el('vaultUnlock').disabled = false;
    el('vaultUnlock').textContent = 'unlock vault';
  }
}

async function doLock() {
  PASSWORD = null;
  await clearSession();
  show('vaultLock');
  hide('vaultMain');
  el('vaultPw').value = '';
  el('vaultLockError').textContent = '';
}

// ── Queue flush ───────────────────────────────────────────────────────────────
async function flushQueue() {
  const resp  = await chrome.runtime.sendMessage({ type: 'GET_QUEUED_ENTRIES' });
  const queue = resp?.entries || [];
  if (!queue.length) return;

  const existingUrls = new Set(vault.map(e => e.url + ':' + e.visitedAt));
  let added = 0;
  for (const entry of queue) {
    const key = entry.url + ':' + entry.visitedAt;
    if (!existingUrls.has(key)) {
      vault.unshift({ ...entry, id: genId(), savedAt: Date.now() });
      existingUrls.add(key);
      added++;
    }
  }
  if (added > 0) {
    await saveVaultEntries(vault, PASSWORD);
    snack(`${added} new entr${added > 1 ? 'ies' : 'y'} added`);
  }
  await chrome.runtime.sendMessage({ type: 'CLEAR_QUEUE' });
  applyFilter();
  renderStats();
  renderAnalytics();
}

// ── Main events ───────────────────────────────────────────────────────────────
function bindMainEvents() {
  el('vaultLockBtn').onclick  = doLock;
  el('vaultSweepBtn').onclick = async () => {
    await chrome.runtime.sendMessage({ type: 'SWEEP_NOW' });
    snack('History sweep complete');
  };
  // Guard pill toggles protection on/off
  el('vaultStatus').onclick = async () => {
    const cfg      = await getConfig();
    const newState = !(cfg.guardEnabled !== false);
    await saveConfig({ guardEnabled: newState });
    el('vaultStatus').textContent = newState ? 'ON' : 'OFF';
    el('vaultStatus').className   = `status-pill${newState ? '' : ' off'}`;
    snack(`Protection ${newState ? 'enabled' : 'disabled'}`);
  };

  // Pivot
  el('vaultPivotHeader').addEventListener('click', e => {
    const tab = e.target.closest('[data-tab]');
    if (!tab) return;
    switchVaultTab(tab.dataset.tab);
  });

  // Filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      page = 1;
      applyFilter();
    };
  });

  // Search
  el('tableSearch').oninput = () => {
    searchQuery = el('tableSearch').value.toLowerCase();
    page = 1;
    applyFilter();
  };

  // Date filters
  el('tableDateFrom').onchange  = () => { page = 1; applyFilter(); };
  el('tableDateTo').onchange    = () => { page = 1; applyFilter(); };
  el('tableClearDates').onclick = () => {
    el('tableDateFrom').value = '';
    el('tableDateTo').value   = '';
    page = 1;
    applyFilter();
  };

  // Sort headers
  document.querySelectorAll('.vault-table th[data-sort]').forEach(th => {
    th.onclick = () => {
      const col = th.dataset.sort;
      if (sortCol === col) { sortDir = sortDir === 'asc' ? 'desc' : 'asc'; }
      else { sortCol = col; sortDir = 'asc'; }
      page = 1;
      applyFilter();
    };
  });

  // Select all
  el('tableSelectAll').onchange = () => {
    const checked = el('tableSelectAll').checked;
    const visible = filtered.slice((page-1)*PAGE_SIZE, page*PAGE_SIZE);
    visible.forEach(e => checked ? selectedIds.add(e.id) : selectedIds.delete(e.id));
    renderTable();
  };

  el('tableDeleteSelected').onclick = doDeleteSelected;
  el('tableClearAll').onclick = () => vaultConfirm(
    'clear entire vault?',
    'All private history will be permanently deleted.',
    async () => {
      await clearVault(PASSWORD);
      vault = [];
      applyFilter();
      renderStats();
      renderAnalytics();
      snack('Vault cleared');
    }
  );
  el('tableExport').onclick = doExport;

  // Domains tab
  el('vaultAddDomainBtn').onclick = doAddDomain;
  el('vaultAddDomain').onkeydown  = e => { if (e.key === 'Enter') doAddDomain(); };
  el('vaultBulkAddBtn').onclick   = doBulkAdd;
  el('vaultDomainSearch').oninput = renderDomainGrid;
  el('vaultClearDomains').onclick = () => vaultConfirm(
    'clear all blocked domains?',
    'All domains will be unblocked.',
    async () => {
      domains = [];
      await saveBlockedDomains([], PASSWORD);
      await updateShadow([]);
      renderDomainGrid();
      snack('All domains cleared');
    }
  );

  // Confirm dialog
  el('vaultConfirmNo').onclick  = () => hide('vaultConfirmDialog');
  el('vaultConfirmYes').onclick = async () => {
    hide('vaultConfirmDialog');
    if (vaultConfirmCallback) { await vaultConfirmCallback(); vaultConfirmCallback = null; }
  };
  el('vaultConfirmDialog').addEventListener('click', e => {
    if (e.target === el('vaultConfirmDialog')) hide('vaultConfirmDialog');
  });
}

// ── Refresh ───────────────────────────────────────────────────────────────────
async function refreshAll() {
  vault   = await getVaultEntries(PASSWORD);
  domains = await getBlockedDomains(PASSWORD);
  applyFilter();
  renderStats();
  renderDomainGrid();
  renderAnalytics();
  await updateShadow(domains);
  const cfg = await getConfig();
  el('vaultStatus').textContent  = cfg.guardEnabled !== false ? 'ON' : 'OFF';
  el('vaultStatus').className    = `status-pill${cfg.guardEnabled !== false ? '' : ' off'}`;
}

// ── Table ─────────────────────────────────────────────────────────────────────
function applyFilter() {
  const dayStart   = new Date(); dayStart.setHours(0,0,0,0);
  const weekStart  = new Date(); weekStart.setDate(weekStart.getDate() - 7);

  // Date range pickers
  const fromRaw = el('tableDateFrom').value;
  const toRaw   = el('tableDateTo').value;
  const fromTs  = fromRaw ? new Date(fromRaw).getTime() : null;
  const toTs    = toRaw   ? new Date(toRaw + 'T23:59:59').getTime() : null;

  filtered = vault.filter(e => {
    if (activeFilter === 'today' && e.visitedAt < dayStart.getTime())  return false;
    if (activeFilter === 'week'  && e.visitedAt < weekStart.getTime()) return false;
    if (fromTs && e.visitedAt < fromTs) return false;
    if (toTs   && e.visitedAt > toTs)   return false;
    if (searchQuery) {
      const hay = ((e.title||'') + ' ' + (e.url||'') + ' ' + (e.domain||'')).toLowerCase();
      if (!hay.includes(searchQuery)) return false;
    }
    return true;
  });

  // Sort
  filtered.sort((a, b) => {
    let va = a[sortCol] || '';
    let vb = b[sortCol] || '';
    if (typeof va === 'string') va = va.toLowerCase();
    if (typeof vb === 'string') vb = vb.toLowerCase();
    if (va < vb) return sortDir === 'asc' ? -1 : 1;
    if (va > vb) return sortDir === 'asc' ?  1 : -1;
    return 0;
  });

  renderTable();
  renderPagination();
  updateSortHeaders();
  el('tableEntryCount').textContent = `${filtered.length} entr${filtered.length !== 1 ? 'ies' : 'y'}`;
}

function renderTable() {
  const tbody   = el('vaultTableBody');
  const start   = (page - 1) * PAGE_SIZE;
  const visible = filtered.slice(start, start + PAGE_SIZE);

  if (!visible.length) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:40px;color:var(--fg-tertiary);">${searchQuery || activeFilter !== 'all' ? 'No results match your filter' : 'Vault is empty'}</td></tr>`;
    el('tableDeleteSelected').disabled = true;
    return;
  }

  tbody.innerHTML = visible.map(e => `
    <tr data-id="${e.id}">
      <td class="col-cb">
        <input type="checkbox" class="row-cb" data-id="${e.id}" ${selectedIds.has(e.id) ? 'checked' : ''} style="accent-color:var(--accent);" />
      </td>
      <td class="col-title">
        <span class="vtitle" data-url="${esc(e.url)}" title="${esc(e.url)}">${esc(e.title || e.domain)}</span>
        <span class="vurl">${esc(e.url)}</span>
      </td>
      <td class="col-domain">
        <span class="vdomain">
          <span class="vdomain-dot"></span>
          ${esc(e.domain)}
        </span>
      </td>
      <td class="col-date"><span class="vdate">${formatFull(e.visitedAt)}</span></td>
      <td class="col-acts">
        <button class="row-del" data-id="${e.id}" title="Delete entry">✕</button>
      </td>
    </tr>
  `).join('');

  tbody.querySelectorAll('.row-cb').forEach(cb => {
    cb.addEventListener('change', () => {
      cb.checked ? selectedIds.add(cb.dataset.id) : selectedIds.delete(cb.dataset.id);
      updateDeleteBtn();
      updateSelectAllState();
    });
  });

  tbody.querySelectorAll('.row-del').forEach(btn => {
    btn.onclick = async () => {
      const id = btn.dataset.id;
      await doDeleteOne(id);
    };
  });

  tbody.querySelectorAll('.vtitle').forEach(span => {
    span.onclick = () => window.open(span.dataset.url, '_blank');
  });

  updateDeleteBtn();
  updateSelectAllState();
}

async function doDeleteOne(id) {
  vault = vault.filter(e => e.id !== id);
  await saveVaultEntries(vault, PASSWORD);
  selectedIds.delete(id);
  applyFilter();
  renderStats();
  renderAnalytics();
  snack('Entry deleted');
}

async function doDeleteSelected() {
  if (!selectedIds.size) return;
  const ids = [...selectedIds];
  vault = vault.filter(e => !ids.includes(e.id));
  await saveVaultEntries(vault, PASSWORD);
  selectedIds.clear();
  applyFilter();
  renderStats();
  renderAnalytics();
  snack(`${ids.length} entr${ids.length !== 1 ? 'ies' : 'y'} deleted`);
}

function updateDeleteBtn() {
  el('tableDeleteSelected').disabled = selectedIds.size === 0;
  if (selectedIds.size > 0) {
    el('tableDeleteSelected').textContent = `delete (${selectedIds.size})`;
  } else {
    el('tableDeleteSelected').textContent = 'delete selected';
  }
}

function updateSelectAllState() {
  const visible = filtered.slice((page-1)*PAGE_SIZE, page*PAGE_SIZE);
  const checkedCount = visible.filter(e => selectedIds.has(e.id)).length;
  const cb = el('tableSelectAll');
  if (!visible.length) { cb.checked = false; cb.indeterminate = false; return; }
  if (checkedCount === visible.length) { cb.checked = true; cb.indeterminate = false; }
  else if (checkedCount === 0)         { cb.checked = false; cb.indeterminate = false; }
  else                                  { cb.indeterminate = true; }
}

function renderPagination() {
  const total = Math.ceil(filtered.length / PAGE_SIZE);
  const el_   = el('vaultPagination');
  if (total <= 1) { el_.innerHTML = ''; return; }

  let html = `<button class="page-btn" id="pgPrev" ${page === 1 ? 'disabled' : ''}>‹</button>`;

  const range = getPaginationRange(page, total);
  range.forEach(p => {
    if (p === '…') {
      html += `<span class="page-info">…</span>`;
    } else {
      html += `<button class="page-btn ${p === page ? 'active' : ''}" data-page="${p}">${p}</button>`;
    }
  });

  html += `<button class="page-btn" id="pgNext" ${page === total ? 'disabled' : ''}>›</button>`;
  html += `<span class="page-info">${page} / ${total}</span>`;
  el_.innerHTML = html;

  el_.querySelectorAll('[data-page]').forEach(btn => {
    btn.onclick = () => { page = parseInt(btn.dataset.page); applyFilter(); };
  });
  const prev = el_.querySelector('#pgPrev');
  const next = el_.querySelector('#pgNext');
  if (prev) prev.onclick = () => { if (page > 1) { page--; applyFilter(); } };
  if (next) next.onclick = () => { if (page < total) { page++; applyFilter(); } };
}

function getPaginationRange(current, total) {
  if (total <= 7) return Array.from({length: total}, (_, i) => i + 1);
  if (current <= 4) return [1, 2, 3, 4, 5, '…', total];
  if (current >= total - 3) return [1, '…', total-4, total-3, total-2, total-1, total];
  return [1, '…', current-1, current, current+1, '…', total];
}

function updateSortHeaders() {
  document.querySelectorAll('.vault-table th[data-sort]').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.sort === sortCol) {
      th.classList.add(sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
    }
  });
}

// ── Stats ─────────────────────────────────────────────────────────────────────
function renderStats() {
  const now   = Date.now();
  const today = new Date(); today.setHours(0,0,0,0);
  const week  = new Date(); week.setDate(week.getDate()-7);

  const todayCount = vault.filter(e => e.visitedAt >= today.getTime()).length;
  const weekCount  = vault.filter(e => e.visitedAt >= week.getTime()).length;

  const statsHtml = [
    { num: vault.length,        lbl: 'total captured', cls: '' },
    { num: domains.length,      lbl: 'domains blocked', cls: '' },
    { num: todayCount,          lbl: 'today',          cls: 'neutral' },
    { num: weekCount,           lbl: 'this week',      cls: 'neutral' },
  ].map(s => `
    <div class="stat-tile ${s.cls}">
      <div class="num">${s.num}</div>
      <div class="lbl">${s.lbl}</div>
    </div>
  `).join('');

  el('statsRow').innerHTML      = statsHtml;
  el('analyticsStats').innerHTML = statsHtml;
}

// ── Domains tab ───────────────────────────────────────────────────────────────
async function doAddDomain() {
  const raw    = el('vaultAddDomain').value.trim();
  const domain = normalizeDomain(raw);
  if (!domain) return snack('Invalid domain', true);
  if (domains.includes(domain)) return snack(`${domain} already blocked`, true);
  domains.push(domain);
  await saveBlockedDomains(domains, PASSWORD);
  await updateShadow(domains);
  el('vaultAddDomain').value = '';
  renderDomainGrid();
  renderStats();
  snack(`${domain} blocked`);
}

async function doBulkAdd() {
  const raw  = el('vaultBulkDomains').value;
  const list = raw.split('\n').map(l => l.trim()).filter(Boolean);
  const added = await addBlockedDomains(list, PASSWORD);
  domains = await getBlockedDomains(PASSWORD);
  await updateShadow(domains);
  el('vaultBulkDomains').value = '';
  renderDomainGrid();
  renderStats();
  snack(`${added.length} domain${added.length !== 1 ? 's' : ''} added`);
}

function renderDomainGrid() {
  const query    = el('vaultDomainSearch').value.toLowerCase();
  const filtered = domains.filter(d => d.includes(query));
  el('vaultDomainCount').textContent = `${filtered.length} domain${filtered.length !== 1 ? 's' : ''}`;
  const grid = el('vaultDomainGrid');

  if (!filtered.length) {
    grid.innerHTML = `<div class="metro-empty" style="padding:40px;grid-column:1/-1;"><div class="metro-empty-icon">🛡</div><div class="metro-empty-text">${query ? 'no match' : 'no blocked domains'}</div></div>`;
    return;
  }

  grid.innerHTML = filtered.map(d => `
    <div class="domain-card">
      <div class="domain-card-letter">${d[0].toUpperCase()}</div>
      <span class="domain-card-name" title="${esc(d)}">${esc(d)}</span>
      <button class="domain-card-del" data-domain="${esc(d)}" title="Unblock">✕</button>
    </div>
  `).join('');

  grid.querySelectorAll('.domain-card-del').forEach(btn => {
    btn.onclick = async () => {
      domains = domains.filter(d => d !== btn.dataset.domain);
      await saveBlockedDomains(domains, PASSWORD);
      await updateShadow(domains);
      renderDomainGrid();
      renderStats();
      snack(`${btn.dataset.domain} unblocked`);
    };
  });
}

// ── Analytics ─────────────────────────────────────────────────────────────────
function renderAnalytics() {
  renderTopDomains();
  renderActivityGrid();
  renderHourChart();
}

function renderTopDomains() {
  const counts = {};
  vault.forEach(e => { counts[e.domain] = (counts[e.domain] || 0) + 1; });
  const sorted = Object.entries(counts).sort((a,b) => b[1]-a[1]).slice(0, 10);
  const max    = sorted[0]?.[1] || 1;

  el('topDomainBars').innerHTML = sorted.map(([d, c]) => `
    <div class="top-domain-bar">
      <span class="tdb-label">${esc(d)}</span>
      <div class="tdb-bar-track">
        <div class="tdb-bar-fill" style="width:${(c/max*100).toFixed(1)}%"></div>
      </div>
      <span class="tdb-count">${c}</span>
    </div>
  `).join('') || '<div class="metro-caption" style="padding:8px 0;">No data yet</div>';
}

function renderActivityGrid() {
  const now      = new Date();
  const monthCounts = {};
  vault.forEach(e => {
    const d = new Date(e.visitedAt);
    const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
    monthCounts[key] = (monthCounts[key] || 0) + 1;
  });

  const cells = [];
  for (let m = 11; m >= 0; m--) {
    const d   = new Date(now.getFullYear(), now.getMonth() - m, 1);
    const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
    const cnt = monthCounts[key] || 0;
    const lvl = cnt === 0 ? '' : cnt < 5 ? 'l1' : cnt < 20 ? 'l2' : cnt < 50 ? 'l3' : 'l4';
    const mon = d.toLocaleString('default', { month: 'short' });
    cells.push(`<div class="activity-cell ${lvl}" title="${mon} ${d.getFullYear()}: ${cnt} visits"></div>`);
  }
  el('activityGrid').innerHTML = cells.join('');
}

function renderHourChart() {
  const hours = Array(24).fill(0);
  vault.forEach(e => {
    const h = new Date(e.visitedAt).getHours();
    hours[h]++;
  });
  const max = Math.max(...hours, 1);

  el('hourChart').innerHTML = hours.map((c, h) => `
    <div style="flex:1;background:var(--accent);opacity:${0.2 + 0.8*(c/max)};height:${Math.max(4, Math.round(c/max*60))}px;" title="${h}:00 — ${c} visits"></div>
  `).join('');
}

// ── Export ────────────────────────────────────────────────────────────────────
function doExport() {
  const data = {
    exportedAt: new Date().toISOString(),
    blockedDomains: domains,
    vaultEntries: vault
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `CHARITRA-export-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  snack('Exported');
}

// ── Shadow domains ────────────────────────────────────────────────────────────
async function updateShadow(d) {
  await chrome.storage.local.set({ hb_blocked_shadow: d });
}

// ── Tab switch ────────────────────────────────────────────────────────────────
function switchVaultTab(tabId) {
  document.querySelectorAll('.vault-pivot-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabId));
  document.querySelectorAll('.vault-panel').forEach(p => p.classList.toggle('active', p.id === `vtab-${tabId}`));
  if (tabId === 'analytics') { renderAnalytics(); }
  if (tabId === 'domains')   { renderDomainGrid(); }
}

// ── Confirm ───────────────────────────────────────────────────────────────────
function vaultConfirm(title, body, cb) {
  el('vaultConfirmTitle').textContent = title;
  el('vaultConfirmBody').textContent  = body;
  vaultConfirmCallback = cb;
  show('vaultConfirmDialog');
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function el(id) { return document.getElementById(id); }
function show(id) { el(id).classList.remove('hidden'); }
function hide(id) { el(id).classList.add('hidden'); }
function esc(s)  { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function toggleReveal(inputId, btnId) {
  const input = el(inputId);
  const isPass = input.type === 'password';
  input.type = isPass ? 'text' : 'password';
  el(btnId).textContent = isPass ? '🙈' : '👁';
}

let snackTimer;
function snack(msg, isError = false) {
  const s = el('vaultSnack');
  s.textContent = msg;
  s.className   = `show${isError ? ' error' : ''}`;
  clearTimeout(snackTimer);
  snackTimer = setTimeout(() => { s.className = ''; }, 3000);
}

function formatFull(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleString();
}

function genId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}
