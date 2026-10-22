# CHARITRA Privacy Policy

Last updated: October 22, 2026

CHARITRA is a Chrome extension for managing browsing history associated
with domains selected by the user. It can remove matching visits from
Chrome history and preserve selected visits in a password-protected
vault.

## Information CHARITRA processes

Depending on your use of the extension, CHARITRA processes:

-   URLs, domains, page titles, and visit timestamps for navigation
    events.
-   A list of domains selected for history protection.
-   Vault entries and extension preferences, including theme,
    scheduling, and automatic-lock settings.
-   Password-verification information and session-expiration data.
-   Temporary queued entries used to transfer captured visits into the
    vault.

The current extension manifest injects a content script on all URLs.
That script reads the current page URL and title and sends them to the
extension's background service worker. The background worker only queues
a visit for vault processing when protection is active and the URL
matches a selected domain. The title-update message is sent on ordinary
pages too, but only updates a matching item already in the queue.

## How information is used

CHARITRA uses this information to detect navigation to protected
domains, remove matching entries from Chrome history, preserve matching
visits in the vault, support search and activity analytics, manage
protected domains, and apply the user's scheduling and session settings.

## Storage and encryption

CHARITRA stores its data using Chrome local extension storage. The vault
entries and saved protected-domain list are encrypted with AES-256-GCM
before being saved by the storage module. The background service worker
also maintains a plaintext list of domain names for matching.

Important implementation detail: the background service worker
temporarily stores queued entries---including URL, domain, title,
timestamp, and sometimes tab ID---in Chrome local storage before the
popup processes them into the encrypted vault. These queued entries are
not encrypted by the queue code itself. This means not all
browsing-related data is encrypted at every stage.

The code uses PBKDF2-SHA256 with 310,000 iterations to derive the
AES-GCM encryption key. However, the password-verification hash in the
inspected version is computed separately as SHA-256 of the salt
concatenated with the password; it does not use PBKDF2. Do not interpret
the encryption-key derivation method as applying to password
verification.

The vault password itself is not saved in persistent storage. A
password-verification hash and salt are saved. Session-expiration
information and extension configuration are also stored locally.

## Data sharing and transmission

The inspected source code does not show a developer-operated server or
network upload for browsing-history data. The content script sends page
URL and title information to the extension's own background service
worker, which is local extension messaging, not an upload to the
developer.

This statement should be rechecked if the extension later adds
analytics, remote services, third-party scripts, or other network
requests.

## Permissions and website access

The current manifest requests History, Storage, Tabs, Web Navigation,
and Alarms permissions, and declares access to all URLs for its content
script. Broad URL access is used by the current implementation to
observe page titles and navigation, then match navigation against the
domains selected by the user. The extension's content script reads the
page URL and title across URLs, so users should understand this access
when installing the extension.

## Retention and deletion

Data remains in extension storage until the user deletes it, resets the
vault, changes the relevant settings, or removes the extension, subject
to Chrome's storage behavior. History cleanup removes matching entries
from Chrome history; it cannot remove records held by websites,
employers, network administrators, or other external systems.

The temporary queue can contain unencrypted browsing entries before they
are processed into the vault. Exported JSON files also contain
unencrypted data and should be stored securely.

If you forget your vault password, it cannot be recovered. Resetting the
vault permanently erases its existing data so you can start again.

## Security limitations

CHARITRA's encryption does not protect against a compromised operating
system or browser, keyloggers, screen recording, or network-level
monitoring. If Chrome Sync synchronizes extension storage, synchronized
encrypted vault blobs may also be copied to other devices.

## Changes to this policy

This policy should be updated whenever CHARITRA's data practices or
functionality change. The published policy should accurately describe
the exact version distributed through the Chrome Web Store.

## Contact and support

Project repository: https://github.com/pramodbeema/charitra Support and
issue tracker: https://github.com/pramodbeema/charitra/issues

------------------------------------------------------------------------

This policy is based on inspection of the provided source archive and is
not an independent security audit. Review it before publication and
ensure it remains accurate for the release submitted to the Chrome Web
Store.
