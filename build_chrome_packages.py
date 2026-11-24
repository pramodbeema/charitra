import os
import zipfile
import shutil

ROOT_DIR = os.path.abspath('.')
UPLOAD_ZIP = os.path.join(ROOT_DIR, "Charitra-Chrome-WebStore-Upload.zip")
CLOUD_ZIP  = os.path.join(ROOT_DIR, "Charitra-Chrome-Cloud-Backup.zip")

# Remove any old builds
for z in [UPLOAD_ZIP, CLOUD_ZIP]:
    if os.path.exists(z):
        os.remove(z)

# -------------------------------------------------------------
# 1. Build Minimal Chrome Web Store Upload ZIP
# -------------------------------------------------------------
runtime_entries = [
    "manifest.json",
    "LICENSE",
    "css",
    "icons",
    "js",
    "pages"
]

print("Building Charitra-Chrome-WebStore-Upload.zip...")
with zipfile.ZipFile(UPLOAD_ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for entry in runtime_entries:
        path = os.path.join(ROOT_DIR, entry)
        if os.path.isfile(path):
            arc = entry.replace('\\', '/')
            zf.write(path, arc)
            print(f" + {arc}")
        elif os.path.isdir(path):
            for r, _, files in os.walk(path):
                for f in sorted(files):
                    f_full = os.path.join(r, f)
                    rel = os.path.relpath(f_full, ROOT_DIR)
                    arc = rel.replace('\\', '/')
                    zf.write(f_full, arc)
                    print(f" + {arc}")

size_kb = os.path.getsize(UPLOAD_ZIP) / 1024
print(f"Done! {UPLOAD_ZIP} ({size_kb:.1f} KB)\n")

# -------------------------------------------------------------
# 2. Build Complete Chrome Cloud Backup ZIP
# -------------------------------------------------------------
backup_entries = [
    "manifest.json",
    "LICENSE",
    "privacy-policy.md",
    "README.md",
    "generate_all_store_assets.py",
    "Charitra-Chrome-WebStore-Upload.zip",
    "css",
    "icons",
    "js",
    "pages",
    "store listing images"
]

print("Building Charitra-Chrome-Cloud-Backup.zip...")
with zipfile.ZipFile(CLOUD_ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for entry in backup_entries:
        path = os.path.join(ROOT_DIR, entry)
        if not os.path.exists(path):
            continue
        if os.path.isfile(path):
            arc = os.path.join("Charitra-Chrome", entry).replace('\\', '/')
            zf.write(path, arc)
            print(f" + {arc}")
        elif os.path.isdir(path):
            for r, _, files in os.walk(path):
                for f in sorted(files):
                    f_full = os.path.join(r, f)
                    rel = os.path.relpath(f_full, ROOT_DIR)
                    arc = os.path.join("Charitra-Chrome", rel).replace('\\', '/')
                    zf.write(f_full, arc)
                    print(f" + {arc}")

size_mb = os.path.getsize(CLOUD_ZIP) / (1024 * 1024)
print(f"\nDone! {CLOUD_ZIP} ({size_mb:.2f} MB)")
