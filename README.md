# CHARITRA

> **Your private browsing history vault** — powered by AES-256-GCM encryption, dressed in Windows Phone / Nokia Lumia Metro style.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue)](LICENSE)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-yellow?logo=googlechrome)](https://github.com/pramodbeema/charitra)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/pramodbeema/charitra/pulls)

---

## What it does

CHARITRA is a Chrome extension that silently removes specific domains from your browser history and stores those visits in an **AES-256-GCM encrypted private vault** that only you can open with a password. The vault data stored on disk is opaque Base64 ciphertext — completely unreadable without the correct password, even if someone opens Chrome's storage files directly.

---

## Features

### 🛡 History Protection
- **Block any domain** — visits are wiped from Chrome history within 1.5 seconds of navigation
- **SPA-aware** — intercepts both full page loads and `history.pushState` changes (React, Vue, Angular apps)
- **Auto-sweep** — periodically scans and clears the last 7 days of history for all blocked domains
- **Manual sweep** — trigger a history sweep instantly from Settings or the vault page
- **Schedule** — set a daily time window (e.g. 09:00–17:00) during which the extension is active; outside those hours, blocked domains pass through unrecorded

### 🔒 Encrypted Vault
- All captured visits (URL, page title, domain, timestamp) are stored encrypted
- **AES-256-GCM** authenticated encryption — both confidentiality and integrity
- **PBKDF2-SHA256** password hashing with 310,000 iterations (OWASP 2023 recommendation)
- Your password is **never stored** — only a salted hash for verification
- Vault is unreadable from Chrome DevTools, `chrome://extensions`, or the filesystem

### 🔍 Advanced Search & Filter
- **Keyword search** — searches page title, URL, and domain simultaneously
- **Date range filter** — pick a from/to date to narrow down captures
- **Quick filters** — All / Today / This Week buttons
- **Sortable columns** — click any column header to sort ascending/descending
- **Pagination** — 50 entries per page with smart ellipsis navigation

### ⊞ Domain Management
- Add single domains by typing or pasting a URL
- **Bulk import** — paste a list of domains (one per line, URLs accepted) and block them all at once
- Search/filter the blocked domain list
- Remove individual domains or clear all at once
- Full domain manager in both the popup and the full vault page

### 🔑 Authentication & Security
- **Auto-unlock** — optional: the vault unlocks the moment you type the correct password (no button press needed). Toggle in Settings
- **Session timeout** — configurable auto-lock after 1–1440 minutes of inactivity
- **Lock on popup close** — vault is locked when you close the popup (configurable)
- **Lock on window blur** — vault locks when Chrome loses focus or you switch windows (configurable)
- **Forgot password** — wipes everything with one confirmed action and lets you start fresh

### 🌗 Themes & Appearance
- **Dark / Light / System** themes — system mode follows your OS `prefers-color-scheme` automatically
- Theme picker on the first-run setup screen so you start with what you like
- **8 Metro accent colors** — Blue (default), Red, Cyan, Green, Purple, Orange, Teal, Pink
- All colors inspired by the Nokia Lumia / Windows Phone color palette

### 📊 Analytics (full vault page)
- **Top blocked domains** — horizontal bar chart of your most-visited blocked sites
- **12-month activity heatmap** — GitHub-style monthly activity grid
- **Hourly chart** — see which hours of the day you visit blocked sites most

### 📤 Export
- Export your entire vault as JSON (re-enter password to confirm)
- Exported file contains blocked domain list + all vault entries with timestamps
- **Note:** exported JSON is unencrypted — store it safely

### 📖 Welcome Page
- Opens automatically on first install
- Feature overview, quick-start guide, security architecture explanation
- **Keyboard shortcut setup guide** — step-by-step instructions with a button that opens `chrome://extensions/shortcuts` directly

### 🎨 Metro UI
- Built from scratch on the **Windows Phone / Nokia Lumia Metro design system**
- **Bebas Neue** bold condensed typeface for headings (same style as superhero movie title cards)
- Segoe UI for body text
- Pivot (tab) navigation, flat tiles, bottom app bar, Metro dialogs, toggle switches
- 380 × 580 px popup + full-page vault tab for power users

---

## Installation

### From Source (Developer Mode)

1. Clone or download this repository:
   ```
   git clone https://github.com/pramodbeema/charitra.git
   ```
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable **Developer mode** (toggle in the top-right corner)
4. Click **Load unpacked**
5. Select the `CHARITRA` folder
6. The CHARITRA icon appears in your toolbar — pin it for easy access

### Set a Keyboard Shortcut (recommended)

1. Go to `chrome://extensions/shortcuts`
2. Find **CHARITRA** in the list
3. Click the edit icon next to "Activate the extension"
4. Press your preferred shortcut (e.g. `Ctrl+Shift+H` on Windows/Linux, `⌘+Shift+H` on macOS)
5. Press your shortcut from any tab to open the vault instantly

---

## First Use

1. **Click the icon** — the first-run setup wizard opens automatically (or opens the welcome page in a new tab)
2. **Pick a theme** — Dark, Light, or System
3. **Set a vault password** — minimum 6 characters. This password cannot be recovered if lost
4. **Add domains to block** — type in the dashboard quick-add box, use the Blocked tab, or bulk-paste a list
5. **Browse normally** — CHARITRA silently cleans up and vaults everything in the background
6. **Open the vault** — unlock the popup and switch to the Vault tab, or click ⊞ for the full-page view

---

## Security Architecture

| Layer | Detail |
|---|---|
| **Encryption** | AES-256-GCM — authenticated encryption (no silent tampering) |
| **Key derivation** | PBKDF2-SHA256, 310,000 iterations, random 16-byte salt per encryption |
| **Password storage** | Never stored — only a PBKDF2 hash + salt for login verification |
| **Data at rest** | All vault entries and blocked domain lists stored as Base64 ciphertext |
| **Shadow list** | A plaintext copy of domain *names only* (no URLs, titles, or timestamps) is kept for the background service worker to match against, without needing the decryption password |
| **Session key** | Held only in JavaScript memory for the popup's lifetime — gone when the popup closes |
| **Filesystem** | Anyone accessing the Chrome profile folder or `chrome.storage.local` files sees only opaque ciphertext |

### What CHARITRA does not protect against

- A compromised Chrome browser or OS-level keylogger
- Screen recording or network-level monitoring
- Chrome Sync (if you sync extensions, encrypted blobs sync too — but they remain encrypted)

For maximum privacy, combine CHARITRA with a VPN and privacy-focused DNS.

---

## File Structure

```
CHARITRA/
├── manifest.json          Chrome MV3 manifest
├── css/
│   └── metro.css          Full Metro design system (themes, components, utilities)
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
├── js/
│   ├── background.js      Service worker — navigation interception, history sweep, queue
│   ├── content.js         (legacy — no longer injected; title fetched via chrome.tabs)
│   ├── crypto.js          AES-256-GCM + PBKDF2 via Web Crypto API
│   ├── popup.js           Popup controller — all UI logic, state, event binding
│   ├── storage.js         Encrypted storage layer — all CRUD through crypto
│   └── vault.js           Full-page vault controller — table, analytics, domain manager
└── pages/
    ├── popup.html         380×580 px popup shell
    ├── vault.html         Full-page vault tab
    └── welcome.html       First-run welcome & feature guide
```

---

## Settings Reference

| Setting | Default | Description |
|---|---|---|
| Block domains from history | ON | Master toggle for history protection |
| Lock vault when popup closes | ON | Clears session when popup window closes |
| Lock vault on window blur | OFF | Locks immediately when Chrome loses focus |
| Auto-sweep on browser start | ON | Sweeps last 7 days of history on startup |
| Auto-unlock as you type | OFF | Unlocks vault without pressing the button once password is correct |
| Session timeout | 30 min | Auto-locks after this many minutes of inactivity |
| Schedule | OFF | Only intercept history during a configured daily time window |
| Theme | Dark | Dark / Light / System |
| Accent color | Blue | 8 Nokia Lumia-inspired colors |

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

[MIT](LICENSE) © [Pramod Beema](https://github.com/pramodbeema)

---

<div align="center">
  <sub>Built with ❤ and the Nokia Lumia spirit &nbsp;·&nbsp; <a href="https://github.com/pramodbeema/charitra">github.com/pramodbeema/CHARITRA</a></sub>
</div>
#
