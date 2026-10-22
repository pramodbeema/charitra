# CHARITRA Privacy Policy

Last updated: October 22, 2026

CHARITRA is a Chrome extension that silently removes visits to user-selected domains from Chrome history and stores those visits in a password-protected, AES-256-GCM encrypted private vault that only the user can unlock.

---

## Information CHARITRA processes

Depending on how you use the extension, CHARITRA processes:

- URLs, domain names, page titles, and visit timestamps for navigation events to domains you have chosen to block.
- Your list of blocked domains.
- Vault entries and extension preferences (theme, accent color, session timeout, schedule, auto-lock settings).
- A password-verification hash and salt used to confirm your vault password. Your password itself is never stored.
- Session-expiration data used to auto-lock the vault after inactivity.
- A temporary queue of captured visits held in local storage while awaiting encryption into the vault.

CHARITRA does **not** inject a content script into web pages. Page titles are retrieved using the `chrome.tabs` API at the moment a navigation to a blocked domain is detected — no script runs inside any website.

---

## How information is used

CHARITRA uses this information solely to:

- Detect navigation to blocked domains in real time.
- Delete matching entries from Chrome history.
- Store matching visits in your encrypted private vault.
- Support vault search, filtering, and activity analytics (visible only to you after unlocking).
- Manage your list of blocked domains.
- Apply your scheduling, session-timeout, and theme settings.

---

## Storage and encryption

All data is stored locally using Chrome's extension storage (`chrome.storage.local`). Nothing is uploaded to any external server.

- **Vault entries and blocked domain lists** are encrypted with AES-256-GCM before being written to storage. The encryption key is derived from your password using PBKDF2-SHA256 with 310,000 iterations and a random 16-byte salt.
- **Your vault password is never stored.** Only a PBKDF2-derived verification hash and its salt are saved for login confirmation.
- **Temporary queue** — captured visits (URL, domain, title, timestamp) are briefly held unencrypted in a queue before the popup processes them into the encrypted vault. This queue is cleared after encryption.
- **Shadow domain list** — the background service worker maintains a plaintext copy of blocked domain names only (no URLs, titles, or timestamps) so it can match navigations without requiring your password.

---

## Data sharing and transmission

CHARITRA does not transmit any browsing data to the developer or any third party. All communication is local extension messaging between the background service worker and the extension's own pages. There are no analytics services, remote APIs, or third-party scripts included.

---

## Permissions

| Permission | Why it is needed |
|---|---|
| `history` | To delete visits to blocked domains from Chrome history and to periodically sweep residual visits from the past 7 days. |
| `storage` | To persist the encrypted vault, blocked domain list, user preferences, and temporary queue — all stored locally on your device. |
| `tabs` | To read the title of the active tab when a navigation to a blocked domain is detected, so vault entries are labelled with a human-readable page title. |
| `webNavigation` | To intercept navigations (including single-page app history changes) in real time, before Chrome records them persistently. |
| `alarms` | To run periodic background tasks: session-expiry checks (every 1 minute) and history sweeps (every 2 minutes). |

CHARITRA does **not** request broad host permissions or inject content scripts into websites. No website's DOM is accessed by the extension.

---

## Retention and deletion

Data remains in extension storage until you delete it manually, reset the vault, or remove the extension. Deleting a blocked domain from the list removes it from future interception but does not retroactively alter Chrome history. Exported JSON files contain unencrypted data and should be stored securely.

**Your vault password cannot be recovered.** If you forget it, the only option is to reset the vault, which permanently erases all stored vault entries.

---

## Security limitations

CHARITRA's encryption does not protect against a compromised operating system or browser, keyloggers, screen recording, or network-level monitoring. If Chrome Sync is enabled and syncs extension storage, encrypted vault blobs may be copied to other signed-in devices — they remain encrypted and unreadable without your password.

---

## Changes to this policy

This policy will be updated whenever CHARITRA's data practices or functionality change. The version published here reflects the exact release distributed through the Chrome Web Store.

---

## Contact and support

Project repository: https://github.com/pramodbeema/charitra  
Issue tracker: https://github.com/pramodbeema/charitra/issues
