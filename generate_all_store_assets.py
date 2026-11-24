import os
import subprocess
import shutil
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUTPUT_DIR = os.path.abspath('store listing images')
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open('icon_b64.txt', 'r') as f:
    ICON_B64 = f.read().strip()

def render_html(html_content, out_filename, width, height):
    temp_html = os.path.abspath(f'temp_{out_filename}.html')
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    out_path = os.path.join(OUTPUT_DIR, out_filename)
    file_url = 'file:///' + temp_html.replace('\\', '/')
    
    cmd = [
        CHROME,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        '--hide-scrollbars',
        '--run-all-compositor-stages-before-draw',
        f'--window-size={width},{height}',
        f'--screenshot={out_path}',
        file_url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if os.path.exists(temp_html):
        try:
            os.remove(temp_html)
        except:
            pass
    
    if not os.path.exists(out_path):
        raise RuntimeError(f"Failed to generate {out_filename}: {res.stderr}")
    
    with Image.open(out_path) as im:
        print(f"Generated: {out_filename} -> size: {im.size}, format: {im.format}")
        if im.size != (width, height):
            raise ValueError(f"Size mismatch: expected ({width},{height}), got {im.size}")
    return out_path

# ==============================================================================
# SCREENSHOT 1: DASHBOARD & ACTIVE PROTECTION (1280x800)
# ==============================================================================
def gen_screenshot_1():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
  body {{
    width: 1280px; height: 800px;
    background: radial-gradient(circle at 50% 12%, #141b27 0%, #090a0e 75%);
    color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
    position: relative; overflow: hidden;
  }}
  .bg-grid {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 32px 32px; pointer-events: none;
  }}
  .bg-glow {{
    position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 650px; height: 380px;
    background: radial-gradient(ellipse at center, rgba(0, 164, 239, 0.22) 0%, rgba(0, 120, 212, 0.08) 50%, transparent 75%);
    filter: blur(40px); pointer-events: none;
  }}
  .header {{ text-align: center; position: absolute; top: 32px; left: 0; right: 0; z-index: 10; }}
  .badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0, 120, 212, 0.16); border: 1px solid rgba(0, 164, 239, 0.4); color: #38bdf8;
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
  }}
  .title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 36px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; color: #ffffff; margin-top: 6px;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.6);
  }}
  .subtitle {{ font-size: 15px; color: #94a3b8; margin-top: 4px; }}
  
  .center-frame {{
    position: absolute; top: 148px; left: 450px; width: 380px; height: 615px;
    background: #111214; border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    box-shadow: 0 25px 65px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(0, 120, 212, 0.28);
    overflow: hidden; display: flex; flex-direction: column; z-index: 5;
  }}
  .win-header {{
    background: #181a1f; border-bottom: 1px solid rgba(255,255,255,0.08); padding: 10px 14px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .win-dots {{ display: flex; gap: 6px; }}
  .win-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .dot-r {{ background: #ef4444; }} .dot-y {{ background: #f59e0b; }} .dot-g {{ background: #10b981; }}
  .win-label {{
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #94a3b8; text-transform: uppercase; display: flex; align-items: center; gap: 6px;
  }}
  .win-label img {{ width: 14px; height: 14px; border-radius: 2px; }}

  .popup-body {{ padding: 16px 18px; flex: 1; display: flex; flex-direction: column; gap: 12px; }}
  .metro-topbar {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }}
  .metro-brand {{ font-family: 'Bahnschrift', sans-serif; font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #ffffff; }}
  .metro-nav {{ display: flex; gap: 12px; font-family: 'Bahnschrift', sans-serif; font-size: 13px; letter-spacing: 1px; text-transform: uppercase; }}
  .nav-item {{ color: #64748b; }}
  .nav-active {{ color: #00a4ef; border-bottom: 2px solid #00a4ef; padding-bottom: 2px; }}

  .status-card {{
    background: linear-gradient(135deg, rgba(0, 120, 212, 0.18), rgba(0, 164, 239, 0.05));
    border: 1px solid rgba(0, 164, 239, 0.3); border-radius: 6px; padding: 12px 14px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .status-info {{ display: flex; align-items: center; gap: 10px; }}
  .pulse-dot {{ width: 10px; height: 10px; background: #10b981; border-radius: 50%; box-shadow: 0 0 10px #10b981; }}
  .status-title {{ font-family: 'Bahnschrift', sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #ffffff; }}
  .status-sub {{ font-size: 11px; color: #94a3b8; }}
  .guard-pill {{ background: #107c10; color: white; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 3px; text-transform: uppercase; }}

  .tab-action-bar {{
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px;
    padding: 10px 12px; display: flex; align-items: center; justify-content: space-between;
  }}
  .tab-domain {{ font-size: 12px; font-weight: 600; color: #e2e8f0; display: flex; align-items: center; gap: 6px; }}
  .btn-block-sm {{
    background: #0078d4; color: white; border: none; font-family: 'Bahnschrift', sans-serif;
    font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 5px 10px; border-radius: 3px;
  }}

  .tiles-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  .metro-tile {{ padding: 12px; border-radius: 4px; display: flex; flex-direction: column; justify-content: space-between; height: 72px; }}
  .tile-accent-1 {{ background: #0078d4; color: white; }}
  .tile-accent-2 {{ background: #005a9e; color: white; }}
  .tile-dark-1 {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); color: #e2e8f0; }}
  .tile-dark-2 {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); color: #e2e8f0; }}
  .tile-num {{ font-family: 'Bahnschrift', sans-serif; font-size: 22px; font-weight: 700; line-height: 1; }}
  .tile-lbl {{ font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; }}

  .recent-section {{ display: flex; flex-direction: column; gap: 6px; flex: 1; }}
  .section-lbl {{ font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px; color: #64748b; text-transform: uppercase; margin-top: 2px; }}
  .capture-item {{
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px;
    padding: 8px 10px; display: flex; align-items: center; justify-content: space-between;
  }}
  .item-left {{ display: flex; flex-direction: column; gap: 2px; }}
  .item-host {{ font-size: 12px; font-weight: 600; color: #38bdf8; }}
  .item-path {{ font-size: 10.5px; color: #64748b; }}
  .item-time {{ font-size: 10.5px; color: #10b981; font-weight: 600; }}

  .side-col {{ position: absolute; top: 170px; width: 320px; display: flex; flex-direction: column; gap: 24px; z-index: 8; }}
  .col-left {{ left: 80px; }} .col-right {{ right: 80px; }}
  .feature-box {{
    background: rgba(18, 22, 30, 0.88); border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #0078d4; border-radius: 8px; padding: 18px 20px;
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.45); backdrop-filter: blur(10px);
  }}
  .f-icon {{ font-size: 22px; margin-bottom: 6px; }}
  .f-title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 15px; font-weight: 700;
    letter-spacing: 1.2px; text-transform: uppercase; color: #ffffff; margin-bottom: 4px;
  }}
  .f-desc {{ font-size: 13px; line-height: 1.45; color: #94a3b8; }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow"></div>
  
  <div class="header">
    <div class="badge">⊞ METRO VAULT DASHBOARD</div>
    <div class="title">PRIVATE BROWSING HISTORY VAULT</div>
    <div class="subtitle">Silently wipes blocked domains from Chrome history into an AES-256 encrypted vault</div>
  </div>

  <div class="side-col col-left">
    <div class="feature-box">
      <div class="f-icon">⚡</div>
      <div class="f-title">1.5s SILENT AUTO-WIPE</div>
      <div class="f-desc">Visits to blocked domains are automatically cleared from Chrome history within 1.5 seconds of navigation.</div>
    </div>
    <div class="feature-box" style="border-left-color: #00a4ef;">
      <div class="f-icon">🔒</div>
      <div class="f-title">AES-256-GCM ENCRYPTED</div>
      <div class="f-desc">Every captured URL, page title, and visit timestamp is sealed inside an authenticated cryptographic vault.</div>
    </div>
  </div>

  <div class="center-frame">
    <div class="win-header">
      <div class="win-dots">
        <div class="win-dot dot-r"></div>
        <div class="win-dot dot-y"></div>
        <div class="win-dot dot-g"></div>
      </div>
      <div class="win-label">
        <img src="data:image/png;base64,{ICON_B64}" />
        CHARITRA VAULT
      </div>
      <div style="width: 30px;"></div>
    </div>

    <div class="popup-body">
      <div class="metro-topbar">
        <div class="metro-brand">CHARITRA</div>
        <div class="metro-nav">
          <span class="nav-active">DASHBOARD</span>
          <span class="nav-item">BLOCKED</span>
          <span class="nav-item">VAULT</span>
          <span class="nav-item">SETTINGS</span>
        </div>
      </div>

      <div class="status-card">
        <div class="status-info">
          <div class="pulse-dot"></div>
          <div>
            <div class="status-title">PROTECTION ACTIVE</div>
            <div class="status-sub">Monitoring 14 blocked domains</div>
          </div>
        </div>
        <div class="guard-pill">ON</div>
      </div>

      <div class="tab-action-bar">
        <div class="tab-domain">
          <span style="color:#00a4ef;">🌐</span>
          <span>github.com</span>
        </div>
        <button class="btn-block-sm">+ BLOCK CURRENT</button>
      </div>

      <div class="tiles-grid">
        <div class="metro-tile tile-accent-1">
          <div class="tile-num">14</div>
          <div class="tile-lbl">BLOCKED SITES</div>
        </div>
        <div class="metro-tile tile-accent-2">
          <div class="tile-num">128</div>
          <div class="tile-lbl">VAULT ENTRIES</div>
        </div>
        <div class="metro-tile tile-dark-1">
          <div class="tile-num" style="color: #38bdf8;">12m</div>
          <div class="tile-lbl">NEXT SWEEP</div>
        </div>
        <div class="metro-tile tile-dark-2">
          <div class="tile-num" style="font-size: 15px; margin-top: 4px; color: #10b981;">09:00-17:00</div>
          <div class="tile-lbl">ACTIVE SCHEDULE</div>
        </div>
      </div>

      <div class="recent-section">
        <div class="section-lbl">RECENT VAULTED CAPTURES</div>
        <div class="capture-item">
          <div class="item-left">
            <div class="item-host">x.com</div>
            <div class="item-path">/notifications</div>
          </div>
          <div class="item-time">2m ago (Wiped)</div>
        </div>
        <div class="capture-item">
          <div class="item-left">
            <div class="item-host">reddit.com</div>
            <div class="item-path">/r/technology</div>
          </div>
          <div class="item-time">14m ago (Wiped)</div>
        </div>
        <div class="capture-item">
          <div class="item-left">
            <div class="item-host">youtube.com</div>
            <div class="item-path">/shorts</div>
          </div>
          <div class="item-time">35m ago (Wiped)</div>
        </div>
      </div>
    </div>
  </div>

  <div class="side-col col-right">
    <div class="feature-box" style="border-left-color: #107c10;">
      <div class="f-icon">⊞</div>
      <div class="f-title">NOKIA LUMIA METRO UI</div>
      <div class="f-desc">Engineered with authentic Windows Phone 8 aesthetic, pivot tab navigation, and live glanceable status tiles.</div>
    </div>
    <div class="feature-box" style="border-left-color: #e51400;">
      <div class="f-icon">🛡️</div>
      <div class="f-title">ZERO-KNOWLEDGE PRIVACY</div>
      <div class="f-desc">Master password is never stored. Local disk files and Chrome storage hold only opaque Base64 ciphertext.</div>
    </div>
  </div>
</body>
</html>"""
    return render_html(html, 'screenshot1_dashboard_1280x800.png', 1280, 800)

# ==============================================================================
# SCREENSHOT 2: DOMAINS & BULK INTERCEPTION (1280x800)
# ==============================================================================
def gen_screenshot_2():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
  body {{
    width: 1280px; height: 800px;
    background: radial-gradient(circle at 50% 12%, #141b27 0%, #090a0e 75%);
    color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
    position: relative; overflow: hidden;
  }}
  .bg-grid {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 32px 32px; pointer-events: none;
  }}
  .bg-glow {{
    position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 650px; height: 380px;
    background: radial-gradient(ellipse at center, rgba(0, 164, 239, 0.22) 0%, rgba(0, 120, 212, 0.08) 50%, transparent 75%);
    filter: blur(40px); pointer-events: none;
  }}
  .header {{ text-align: center; position: absolute; top: 32px; left: 0; right: 0; z-index: 10; }}
  .badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0, 120, 212, 0.16); border: 1px solid rgba(0, 164, 239, 0.4); color: #38bdf8;
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
  }}
  .title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 36px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; color: #ffffff; margin-top: 6px;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.6);
  }}
  .subtitle {{ font-size: 15px; color: #94a3b8; margin-top: 4px; }}
  
  .center-frame {{
    position: absolute; top: 148px; left: 450px; width: 380px; height: 615px;
    background: #111214; border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    box-shadow: 0 25px 65px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(0, 120, 212, 0.28);
    overflow: hidden; display: flex; flex-direction: column; z-index: 5;
  }}
  .win-header {{
    background: #181a1f; border-bottom: 1px solid rgba(255,255,255,0.08); padding: 10px 14px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .win-dots {{ display: flex; gap: 6px; }}
  .win-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .dot-r {{ background: #ef4444; }} .dot-y {{ background: #f59e0b; }} .dot-g {{ background: #10b981; }}
  .win-label {{
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #94a3b8; text-transform: uppercase; display: flex; align-items: center; gap: 6px;
  }}
  .win-label img {{ width: 14px; height: 14px; border-radius: 2px; }}

  .popup-body {{ padding: 16px 18px; flex: 1; display: flex; flex-direction: column; gap: 12px; }}
  .metro-topbar {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }}
  .metro-brand {{ font-family: 'Bahnschrift', sans-serif; font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #ffffff; }}
  .metro-nav {{ display: flex; gap: 12px; font-family: 'Bahnschrift', sans-serif; font-size: 13px; letter-spacing: 1px; text-transform: uppercase; }}
  .nav-item {{ color: #64748b; }}
  .nav-active {{ color: #00a4ef; border-bottom: 2px solid #00a4ef; padding-bottom: 2px; }}

  /* Add domain bar */
  .add-domain-box {{
    display: flex; gap: 6px;
  }}
  .domain-input {{
    flex: 1; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 4px; padding: 8px 12px; color: white; font-size: 12px;
  }}
  .btn-add {{
    background: #0078d4; color: white; border: none; border-radius: 4px;
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 1px; padding: 8px 12px; cursor: pointer; text-transform: uppercase;
  }}

  /* Bulk import toggle bar */
  .bulk-bar {{
    background: rgba(255,255,255,0.02); border: 1px dashed rgba(0, 164, 239, 0.4);
    border-radius: 4px; padding: 7px 10px; display: flex; align-items: center; justify-content: space-between;
    font-size: 11px; color: #38bdf8;
  }}

  /* Domain List */
  .domains-list {{
    display: flex; flex-direction: column; gap: 6px; flex: 1;
  }}
  .domain-row {{
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px; padding: 8px 12px; display: flex; align-items: center; justify-content: space-between;
  }}
  .d-left {{ display: flex; align-items: center; gap: 8px; }}
  .d-icon {{ font-size: 14px; color: #00a4ef; }}
  .d-name {{ font-size: 12.5px; font-weight: 600; color: #f8fafc; }}
  .d-status {{ font-size: 10px; color: #10b981; text-transform: uppercase; }}
  .d-actions {{ display: flex; align-items: center; gap: 10px; }}
  .toggle-switch {{
    width: 28px; height: 16px; background: #0078d4; border-radius: 10px; position: relative;
  }}
  .toggle-switch::after {{
    content: ''; position: absolute; width: 12px; height: 12px; background: white;
    border-radius: 50%; right: 2px; top: 2px;
  }}
  .del-btn {{ color: #ef4444; font-size: 12px; opacity: 0.8; }}

  /* Sweep bar footer */
  .sweep-footer {{
    background: linear-gradient(135deg, rgba(0, 120, 212, 0.15), rgba(0, 164, 239, 0.05));
    border: 1px solid rgba(0, 164, 239, 0.25); border-radius: 6px; padding: 10px 12px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .sweep-txt {{ font-size: 11px; color: #cbd5e1; }}
  .btn-sweep {{
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
    color: white; font-family: 'Bahnschrift', sans-serif; font-size: 10.5px; font-weight: 700;
    padding: 4px 10px; border-radius: 3px; text-transform: uppercase;
  }}

  .side-col {{ position: absolute; top: 170px; width: 320px; display: flex; flex-direction: column; gap: 24px; z-index: 8; }}
  .col-left {{ left: 80px; }} .col-right {{ right: 80px; }}
  .feature-box {{
    background: rgba(18, 22, 30, 0.88); border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #0078d4; border-radius: 8px; padding: 18px 20px;
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.45); backdrop-filter: blur(10px);
  }}
  .f-icon {{ font-size: 22px; margin-bottom: 6px; }}
  .f-title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 15px; font-weight: 700;
    letter-spacing: 1.2px; text-transform: uppercase; color: #ffffff; margin-bottom: 4px;
  }}
  .f-desc {{ font-size: 13px; line-height: 1.45; color: #94a3b8; }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow"></div>
  
  <div class="header">
    <div class="badge">🛡️ DOMAIN MANAGEMENT</div>
    <div class="title">SILENT DOMAIN INTERCEPTION & SCRUBBING</div>
    <div class="subtitle">Instant single-domain block, bulk URL import, and automatic 7-day history sweep</div>
  </div>

  <div class="side-col col-left">
    <div class="feature-box" style="border-left-color: #00a4ef;">
      <div class="f-icon">📋</div>
      <div class="f-title">BULK DOMAIN IMPORT</div>
      <div class="f-desc">Paste dozens of URLs or raw domain lists to block them all in one single action without manual entry.</div>
    </div>
    <div class="feature-box" style="border-left-color: #107c10;">
      <div class="f-icon">🧹</div>
      <div class="f-title">7-DAY AUTO-SWEEP</div>
      <div class="f-desc">Silently scans and removes historical visits for all blocked domains across the past 7 days periodically.</div>
    </div>
  </div>

  <div class="center-frame">
    <div class="win-header">
      <div class="win-dots">
        <div class="win-dot dot-r"></div>
        <div class="win-dot dot-y"></div>
        <div class="win-dot dot-g"></div>
      </div>
      <div class="win-label">
        <img src="data:image/png;base64,{ICON_B64}" />
        CHARITRA VAULT
      </div>
      <div style="width: 30px;"></div>
    </div>

    <div class="popup-body">
      <div class="metro-topbar">
        <div class="metro-brand">CHARITRA</div>
        <div class="metro-nav">
          <span class="nav-item">DASHBOARD</span>
          <span class="nav-active">BLOCKED</span>
          <span class="nav-item">VAULT</span>
          <span class="nav-item">SETTINGS</span>
        </div>
      </div>

      <div class="add-domain-box">
        <input class="domain-input" type="text" value="reddit.com" readonly />
        <button class="btn-add">+ BLOCK</button>
      </div>

      <div class="bulk-bar">
        <span>📋 Bulk Import Domains / URLs</span>
        <span style="font-weight:700;">[PASTE LIST]</span>
      </div>

      <div class="domains-list">
        <div class="domain-row">
          <div class="d-left">
            <span class="d-icon">🔒</span>
            <div>
              <div class="d-name">reddit.com</div>
              <div class="d-status">Active Interception</div>
            </div>
          </div>
          <div class="d-actions">
            <div class="toggle-switch"></div>
            <span class="del-btn">✕</span>
          </div>
        </div>

        <div class="domain-row">
          <div class="d-left">
            <span class="d-icon">🔒</span>
            <div>
              <div class="d-name">x.com</div>
              <div class="d-status">Active Interception</div>
            </div>
          </div>
          <div class="d-actions">
            <div class="toggle-switch"></div>
            <span class="del-btn">✕</span>
          </div>
        </div>

        <div class="domain-row">
          <div class="d-left">
            <span class="d-icon">🔒</span>
            <div>
              <div class="d-name">youtube.com</div>
              <div class="d-status">Active Interception</div>
            </div>
          </div>
          <div class="d-actions">
            <div class="toggle-switch"></div>
            <span class="del-btn">✕</span>
          </div>
        </div>

        <div class="domain-row">
          <div class="d-left">
            <span class="d-icon">🔒</span>
            <div>
              <div class="d-name">instagram.com</div>
              <div class="d-status">Active Interception</div>
            </div>
          </div>
          <div class="d-actions">
            <div class="toggle-switch"></div>
            <span class="del-btn">✕</span>
          </div>
        </div>

        <div class="domain-row">
          <div class="d-left">
            <span class="d-icon">🔒</span>
            <div>
              <div class="d-name">netflix.com</div>
              <div class="d-status">Active Interception</div>
            </div>
          </div>
          <div class="d-actions">
            <div class="toggle-switch"></div>
            <span class="del-btn">✕</span>
          </div>
        </div>

        <div class="domain-row">
          <div class="d-left">
            <span class="d-icon">🔒</span>
            <div>
              <div class="d-name">tiktok.com</div>
              <div class="d-status">Active Interception</div>
            </div>
          </div>
          <div class="d-actions">
            <div class="toggle-switch"></div>
            <span class="del-btn">✕</span>
          </div>
        </div>
      </div>

      <div class="sweep-footer">
        <div class="sweep-txt">Next sweep: <strong>18 mins</strong></div>
        <button class="btn-sweep">🧹 SWEEP NOW</button>
      </div>
    </div>
  </div>

  <div class="side-col col-right">
    <div class="feature-box" style="border-left-color: #0078d4;">
      <div class="f-icon">🔄</div>
      <div class="f-title">SPA & PUSHSTATE AWARE</div>
      <div class="f-desc">Accurately catches and scrubs dynamic route transitions in React, Vue, and Angular applications.</div>
    </div>
    <div class="feature-box" style="border-left-color: #e51400;">
      <div class="f-icon">⚡</div>
      <div class="f-title">SUB-SECOND SCRUBBING</div>
      <div class="f-desc">Erases history records within 1.5 seconds, ensuring your browsing traces never persist in history.</div>
    </div>
  </div>
</body>
</html>"""
    return render_html(html, 'screenshot2_domains_1280x800.png', 1280, 800)

# ==============================================================================
# SCREENSHOT 3: ENCRYPTION & SECURITY (1280x800)
# ==============================================================================
def gen_screenshot_3():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
  body {{
    width: 1280px; height: 800px;
    background: radial-gradient(circle at 50% 12%, #141b27 0%, #090a0e 75%);
    color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
    position: relative; overflow: hidden;
  }}
  .bg-grid {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 32px 32px; pointer-events: none;
  }}
  .bg-glow {{
    position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 650px; height: 380px;
    background: radial-gradient(ellipse at center, rgba(0, 164, 239, 0.22) 0%, rgba(0, 120, 212, 0.08) 50%, transparent 75%);
    filter: blur(40px); pointer-events: none;
  }}
  .header {{ text-align: center; position: absolute; top: 32px; left: 0; right: 0; z-index: 10; }}
  .badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0, 120, 212, 0.16); border: 1px solid rgba(0, 164, 239, 0.4); color: #38bdf8;
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
  }}
  .title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 36px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; color: #ffffff; margin-top: 6px;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.6);
  }}
  .subtitle {{ font-size: 15px; color: #94a3b8; margin-top: 4px; }}
  
  .center-frame {{
    position: absolute; top: 148px; left: 450px; width: 380px; height: 615px;
    background: #111214; border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    box-shadow: 0 25px 65px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(0, 120, 212, 0.28);
    overflow: hidden; display: flex; flex-direction: column; z-index: 5;
  }}
  .win-header {{
    background: #181a1f; border-bottom: 1px solid rgba(255,255,255,0.08); padding: 10px 14px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .win-dots {{ display: flex; gap: 6px; }}
  .win-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .dot-r {{ background: #ef4444; }} .dot-y {{ background: #f59e0b; }} .dot-g {{ background: #10b981; }}
  .win-label {{
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #94a3b8; text-transform: uppercase; display: flex; align-items: center; gap: 6px;
  }}
  .win-label img {{ width: 14px; height: 14px; border-radius: 2px; }}

  .popup-body {{
    padding: 24px 20px; flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: space-between; text-align: center;
  }}
  .lock-shield {{
    width: 64px; height: 64px; margin-bottom: 8px; filter: drop-shadow(0 0 16px rgba(0, 164, 239, 0.5));
  }}
  .lock-title {{
    font-family: 'Bahnschrift', sans-serif; font-size: 24px; font-weight: 700;
    letter-spacing: 2px; color: #ffffff; text-transform: uppercase;
  }}
  .lock-sub {{ font-size: 12px; color: #94a3b8; margin-top: 4px; margin-bottom: 16px; max-width: 280px; }}
  
  .pw-box {{
    width: 100%; display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px;
  }}
  .pw-input-wrap {{
    position: relative; width: 100%;
  }}
  .pw-input {{
    width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.15);
    border-radius: 4px; padding: 10px 14px; color: white; font-size: 15px; letter-spacing: 3px;
    text-align: center;
  }}
  .btn-unlock {{
    width: 100%; background: #0078d4; color: white; border: none; border-radius: 4px;
    font-family: 'Bahnschrift', sans-serif; font-size: 13px; font-weight: 700;
    letter-spacing: 1.5px; padding: 10px; cursor: pointer; text-transform: uppercase;
    box-shadow: 0 4px 14px rgba(0, 120, 212, 0.4);
  }}

  /* Crypto Specs Card */
  .crypto-specs {{
    width: 100%; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 6px; padding: 12px 14px; text-align: left; display: flex; flex-direction: column; gap: 6px;
  }}
  .spec-row {{ display: flex; justify-content: space-between; font-size: 11px; }}
  .spec-key {{ color: #64748b; text-transform: uppercase; font-weight: 600; }}
  .spec-val {{ color: #38bdf8; font-family: monospace; font-weight: 600; }}

  .forgot-txt {{ font-size: 10.5px; color: #64748b; margin-top: 8px; }}

  .side-col {{ position: absolute; top: 170px; width: 320px; display: flex; flex-direction: column; gap: 24px; z-index: 8; }}
  .col-left {{ left: 80px; }} .col-right {{ right: 80px; }}
  .feature-box {{
    background: rgba(18, 22, 30, 0.88); border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #0078d4; border-radius: 8px; padding: 18px 20px;
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.45); backdrop-filter: blur(10px);
  }}
  .f-icon {{ font-size: 22px; margin-bottom: 6px; }}
  .f-title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 15px; font-weight: 700;
    letter-spacing: 1.2px; text-transform: uppercase; color: #ffffff; margin-bottom: 4px;
  }}
  .f-desc {{ font-size: 13px; line-height: 1.45; color: #94a3b8; }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow"></div>
  
  <div class="header">
    <div class="badge">🔒 ZERO-KNOWLEDGE CRYPTOGRAPHY</div>
    <div class="title">MILITARY-GRADE AES-256-GCM ENCRYPTION</div>
    <div class="subtitle">Opaque Base64 ciphertext on disk. Passwords never stored. OWASP 2023 certified.</div>
  </div>

  <div class="side-col col-left">
    <div class="feature-box" style="border-left-color: #00a4ef;">
      <div class="f-icon">🛡️</div>
      <div class="f-title">OWASP 310,000 ITERATIONS</div>
      <div class="f-desc">Key derivation powered by PBKDF2-SHA256 with 310,000 rounds protects against brute-force attacks.</div>
    </div>
    <div class="feature-box" style="border-left-color: #107c10;">
      <div class="f-icon">⏱️</div>
      <div class="f-title">CONFIGURABLE AUTO-LOCK</div>
      <div class="f-desc">Locks instantly on window blur, popup close, or idle timeout so your private vault remains secure.</div>
    </div>
  </div>

  <div class="center-frame">
    <div class="win-header">
      <div class="win-dots">
        <div class="win-dot dot-r"></div>
        <div class="win-dot dot-y"></div>
        <div class="win-dot dot-g"></div>
      </div>
      <div class="win-label">
        <img src="data:image/png;base64,{ICON_B64}" />
        CHARITRA VAULT
      </div>
      <div style="width: 30px;"></div>
    </div>

    <div class="popup-body">
      <div>
        <img class="lock-shield" src="data:image/png;base64,{ICON_B64}" />
        <div class="lock-title">VAULT LOCKED</div>
        <div class="lock-sub">Enter master password to decrypt your private browsing session</div>
      </div>

      <div class="pw-box">
        <div class="pw-input-wrap">
          <input class="pw-input" type="password" value="MasterPassword123" readonly />
        </div>
        <button class="btn-unlock">🔓 UNLOCK VAULT</button>
      </div>

      <div class="crypto-specs">
        <div class="spec-row">
          <span class="spec-key">Encryption:</span>
          <span class="spec-val">AES-256-GCM (Auth)</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Derivation:</span>
          <span class="spec-val">PBKDF2-SHA256 (310k)</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Salt:</span>
          <span class="spec-val">16-Byte Cryptographic</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Storage:</span>
          <span class="spec-val">Opaque Base64 Blob</span>
        </div>
      </div>

      <div class="forgot-txt">
        Forgot password? Emergency full wipe safeguard protects privacy.
      </div>
    </div>
  </div>

  <div class="side-col col-right">
    <div class="feature-box" style="border-left-color: #0078d4;">
      <div class="f-icon">💾</div>
      <div class="f-title">CIPHERTEXT AT REST</div>
      <div class="f-desc">Raw disk files contain only encrypted blobs. Inspected storage reveals zero plaintext URLs or titles.</div>
    </div>
    <div class="feature-box" style="border-left-color: #e51400;">
      <div class="f-icon">🔑</div>
      <div class="f-title">ZERO-KNOWLEDGE PRIVACY</div>
      <div class="f-desc">Master password is never transmitted or stored anywhere. Only you hold the decryption key.</div>
    </div>
  </div>
</body>
</html>"""
    return render_html(html, 'screenshot3_security_1280x800.png', 1280, 800)

# ==============================================================================
# SCREENSHOT 4: METRO THEMES & CUSTOMIZATION (1280x800)
# ==============================================================================
def gen_screenshot_4():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
  body {{
    width: 1280px; height: 800px;
    background: radial-gradient(circle at 50% 12%, #141b27 0%, #090a0e 75%);
    color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
    position: relative; overflow: hidden;
  }}
  .bg-grid {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 32px 32px; pointer-events: none;
  }}
  .bg-glow {{
    position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 650px; height: 380px;
    background: radial-gradient(ellipse at center, rgba(0, 164, 239, 0.22) 0%, rgba(0, 120, 212, 0.08) 50%, transparent 75%);
    filter: blur(40px); pointer-events: none;
  }}
  .header {{ text-align: center; position: absolute; top: 32px; left: 0; right: 0; z-index: 10; }}
  .badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0, 120, 212, 0.16); border: 1px solid rgba(0, 164, 239, 0.4); color: #38bdf8;
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
  }}
  .title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 36px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; color: #ffffff; margin-top: 6px;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.6);
  }}
  .subtitle {{ font-size: 15px; color: #94a3b8; margin-top: 4px; }}
  
  .center-frame {{
    position: absolute; top: 148px; left: 450px; width: 380px; height: 615px;
    background: #111214; border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    box-shadow: 0 25px 65px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(0, 120, 212, 0.28);
    overflow: hidden; display: flex; flex-direction: column; z-index: 5;
  }}
  .win-header {{
    background: #181a1f; border-bottom: 1px solid rgba(255,255,255,0.08); padding: 10px 14px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .win-dots {{ display: flex; gap: 6px; }}
  .win-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .dot-r {{ background: #ef4444; }} .dot-y {{ background: #f59e0b; }} .dot-g {{ background: #10b981; }}
  .win-label {{
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #94a3b8; text-transform: uppercase; display: flex; align-items: center; gap: 6px;
  }}
  .win-label img {{ width: 14px; height: 14px; border-radius: 2px; }}

  .popup-body {{ padding: 16px 18px; flex: 1; display: flex; flex-direction: column; gap: 14px; }}
  .metro-topbar {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 8px; }}
  .metro-brand {{ font-family: 'Bahnschrift', sans-serif; font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #ffffff; }}
  .metro-nav {{ display: flex; gap: 12px; font-family: 'Bahnschrift', sans-serif; font-size: 13px; letter-spacing: 1px; text-transform: uppercase; }}
  .nav-item {{ color: #64748b; }}
  .nav-active {{ color: #00a4ef; border-bottom: 2px solid #00a4ef; padding-bottom: 2px; }}

  .section-hdr {{
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #64748b; text-transform: uppercase; margin-bottom: 6px;
  }}

  /* Theme Switcher */
  .theme-btns {{ display: flex; gap: 6px; }}
  .btn-theme {{
    flex: 1; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    color: #94a3b8; font-family: 'Bahnschrift', sans-serif; font-size: 11px; font-weight: 700;
    padding: 8px; border-radius: 4px; text-align: center; text-transform: uppercase;
  }}
  .btn-theme-active {{
    background: #0078d4; border-color: #00a4ef; color: white;
  }}

  /* 8 Lumia Accent Colors */
  .accents-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px;
  }}
  .swatch {{
    height: 38px; border-radius: 4px; display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: white; cursor: pointer;
  }}
  .sw-active {{ outline: 2px solid white; outline-offset: 1px; }}

  /* Settings Toggles */
  .setting-row {{
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px; padding: 10px 12px; display: flex; align-items: center; justify-content: space-between;
  }}
  .s-left {{ display: flex; flex-direction: column; gap: 2px; }}
  .s-name {{ font-size: 12px; font-weight: 600; color: #f8fafc; }}
  .s-desc {{ font-size: 10.5px; color: #64748b; }}
  .mini-toggle {{
    width: 28px; height: 16px; background: #0078d4; border-radius: 10px; position: relative;
  }}
  .mini-toggle::after {{
    content: ''; position: absolute; width: 12px; height: 12px; background: white;
    border-radius: 50%; right: 2px; top: 2px;
  }}

  .side-col {{ position: absolute; top: 170px; width: 320px; display: flex; flex-direction: column; gap: 24px; z-index: 8; }}
  .col-left {{ left: 80px; }} .col-right {{ right: 80px; }}
  .feature-box {{
    background: rgba(18, 22, 30, 0.88); border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #0078d4; border-radius: 8px; padding: 18px 20px;
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.45); backdrop-filter: blur(10px);
  }}
  .f-icon {{ font-size: 22px; margin-bottom: 6px; }}
  .f-title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 15px; font-weight: 700;
    letter-spacing: 1.2px; text-transform: uppercase; color: #ffffff; margin-bottom: 4px;
  }}
  .f-desc {{ font-size: 13px; line-height: 1.45; color: #94a3b8; }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow"></div>
  
  <div class="header">
    <div class="badge">🎨 METRO STYLING & ACCENTS</div>
    <div class="title">AUTHENTIC NOKIA LUMIA METRO THEMES</div>
    <div class="subtitle">Personalize your vault with Dark, Light, System themes and 8 signature Lumia accent colors</div>
  </div>

  <div class="side-col col-left">
    <div class="feature-box" style="border-left-color: #00a4ef;">
      <div class="f-icon">📱</div>
      <div class="f-title">WINDOWS PHONE LEGACY</div>
      <div class="f-desc">A nostalgic, polished tribute to the clean lines and iconic flat design of Windows Phone 8 & Nokia Lumia.</div>
    </div>
    <div class="feature-box" style="border-left-color: #107c10;">
      <div class="f-icon">🌗</div>
      <div class="f-title">DYNAMIC SYSTEM SYNC</div>
      <div class="f-desc">Automatically adapts between dark and light themes following your operating system preferences.</div>
    </div>
  </div>

  <div class="center-frame">
    <div class="win-header">
      <div class="win-dots">
        <div class="win-dot dot-r"></div>
        <div class="win-dot dot-y"></div>
        <div class="win-dot dot-g"></div>
      </div>
      <div class="win-label">
        <img src="data:image/png;base64,{ICON_B64}" />
        CHARITRA VAULT
      </div>
      <div style="width: 30px;"></div>
    </div>

    <div class="popup-body">
      <div class="metro-topbar">
        <div class="metro-brand">CHARITRA</div>
        <div class="metro-nav">
          <span class="nav-item">DASHBOARD</span>
          <span class="nav-item">BLOCKED</span>
          <span class="nav-item">VAULT</span>
          <span class="nav-active">SETTINGS</span>
        </div>
      </div>

      <div>
        <div class="section-hdr">APPEARANCE THEME</div>
        <div class="theme-btns">
          <div class="btn-theme btn-theme-active">DARK ✓</div>
          <div class="btn-theme">LIGHT</div>
          <div class="btn-theme">SYSTEM</div>
        </div>
      </div>

      <div>
        <div class="section-hdr">8 LUMIA ACCENT COLORS</div>
        <div class="accents-grid">
          <div class="swatch sw-active" style="background:#0078d4;">BLUE</div>
          <div class="swatch" style="background:#e51400;">RED</div>
          <div class="swatch" style="background:#00a4ef;">CYAN</div>
          <div class="swatch" style="background:#107c10;">GREEN</div>
          <div class="swatch" style="background:#744da9;">PURPLE</div>
          <div class="swatch" style="background:#ff8c00;">ORANGE</div>
          <div class="swatch" style="background:#008272;">TEAL</div>
          <div class="swatch" style="background:#e3008c;">PINK</div>
        </div>
      </div>

      <div>
        <div class="section-hdr">SECURITY PREFERENCES</div>
        <div style="display:flex; flex-direction:column; gap:6px;">
          <div class="setting-row">
            <div class="s-left">
              <div class="s-name">Auto-Unlock on Correct Password</div>
              <div class="s-desc">Unlocks immediately without pressing Enter</div>
            </div>
            <div class="mini-toggle"></div>
          </div>
          <div class="setting-row">
            <div class="s-left">
              <div class="s-name">Lock on Window Blur</div>
              <div class="s-desc">Locks when switching tabs or apps</div>
            </div>
            <div class="mini-toggle"></div>
          </div>
          <div class="setting-row">
            <div class="s-left">
              <div class="s-name">Active Schedule Window</div>
              <div class="s-desc">Daily protection active: 09:00 - 17:00</div>
            </div>
            <div class="mini-toggle"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="side-col col-right">
    <div class="feature-box" style="border-left-color: #ff8c00;">
      <div class="f-icon">🎨</div>
      <div class="f-title">8 SIGNATURE ACCENTS</div>
      <div class="f-desc">Handpicked Lumia color swatches let you personalize your vault to match your unique desktop setup.</div>
    </div>
    <div class="feature-box" style="border-left-color: #744da9;">
      <div class="f-icon">⏰</div>
      <div class="f-title">SCHEDULED PRIVACY</div>
      <div class="f-desc">Define specific active hours (e.g. work hours) for automatic zero-trace interception and history sweeping.</div>
    </div>
  </div>
</body>
</html>"""
    return render_html(html, 'screenshot4_themes_1280x800.png', 1280, 800)

# ==============================================================================
# SCREENSHOT 5: FULL-PAGE VAULT & ANALYTICS (1280x800)
# ==============================================================================
def gen_screenshot_5():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
  body {{
    width: 1280px; height: 800px;
    background: radial-gradient(circle at 50% 12%, #141b27 0%, #090a0e 75%);
    color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
    position: relative; overflow: hidden;
  }}
  .bg-grid {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 32px 32px; pointer-events: none;
  }}
  .bg-glow {{
    position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 650px; height: 380px;
    background: radial-gradient(ellipse at center, rgba(0, 164, 239, 0.22) 0%, rgba(0, 120, 212, 0.08) 50%, transparent 75%);
    filter: blur(40px); pointer-events: none;
  }}
  .header {{ text-align: center; position: absolute; top: 26px; left: 0; right: 0; z-index: 10; }}
  .badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0, 120, 212, 0.16); border: 1px solid rgba(0, 164, 239, 0.4); color: #38bdf8;
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; padding: 4px 16px; border-radius: 20px;
  }}
  .title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 34px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; color: #ffffff; margin-top: 5px;
    text-shadow: 0 2px 14px rgba(0, 0, 0, 0.6);
  }}
  .subtitle {{ font-size: 14.5px; color: #94a3b8; margin-top: 3px; }}
  
  /* Widescreen Vault Tab Frame */
  .vault-frame {{
    position: absolute; top: 125px; left: 160px; width: 960px; height: 575px;
    background: #111214; border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    box-shadow: 0 25px 70px -15px rgba(0, 0, 0, 0.95), 0 0 40px rgba(0, 120, 212, 0.28);
    overflow: hidden; display: flex; flex-direction: column; z-index: 5;
  }}
  .win-header {{
    background: #181a1f; border-bottom: 1px solid rgba(255,255,255,0.08); padding: 10px 18px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .win-dots {{ display: flex; gap: 6px; }}
  .win-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .dot-r {{ background: #ef4444; }} .dot-y {{ background: #f59e0b; }} .dot-g {{ background: #10b981; }}
  .win-url {{
    background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px;
    padding: 3px 18px; font-size: 11.5px; color: #94a3b8; display: flex; align-items: center; gap: 8px;
  }}

  .vault-content {{ padding: 18px 24px; flex: 1; display: flex; flex-direction: column; gap: 14px; }}
  .vault-top-bar {{ display: flex; justify-content: space-between; align-items: center; }}
  .v-title {{ font-family: 'Bahnschrift', sans-serif; font-size: 22px; font-weight: 700; letter-spacing: 2px; color: white; }}
  .v-search-bar {{ display: flex; gap: 8px; align-items: center; }}
  .v-search-input {{
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12); border-radius: 4px;
    padding: 6px 12px; color: white; font-size: 12px; width: 220px;
  }}
  .v-btn {{
    background: #0078d4; color: white; border: none; border-radius: 4px; padding: 6px 12px;
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase;
  }}

  /* Analytics Grid: 2 columns */
  .analytics-grid {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 14px; }}
  .chart-card {{
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px;
    padding: 12px 16px;
  }}
  .chart-title {{
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #94a3b8; text-transform: uppercase; margin-bottom: 8px;
  }}
  .bar-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; font-size: 11px; }}
  .bar-label {{ width: 90px; color: #cbd5e1; font-weight: 600; text-align: right; }}
  .bar-track {{ flex: 1; height: 10px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 2px; }}
  .bar-val {{ width: 25px; color: #38bdf8; font-weight: 700; }}

  .stats-col {{ display: flex; flex-direction: column; gap: 8px; }}
  .stat-mini {{
    background: rgba(0, 120, 212, 0.12); border: 1px solid rgba(0, 164, 239, 0.25);
    border-radius: 6px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center;
  }}
  .stat-num {{ font-family: 'Bahnschrift', sans-serif; font-size: 24px; font-weight: 700; color: #38bdf8; }}
  .stat-lbl {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; }}

  /* Heatmap */
  .heatmap-card {{
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px;
    padding: 12px 16px;
  }}
  .heatmap-grid {{
    display: grid; grid-template-columns: repeat(42, 1fr); gap: 3.5px; margin-top: 6px;
  }}
  .hm-cell {{ height: 9px; border-radius: 1px; }}
  .c-0 {{ background: rgba(255,255,255,0.04); }}
  .c-1 {{ background: #004d80; }}
  .c-2 {{ background: #0078d4; }}
  .c-3 {{ background: #00a4ef; }}
  .c-4 {{ background: #38bdf8; }}

  /* Encrypted table */
  .v-table {{
    width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 2px;
  }}
  .v-table th {{
    text-align: left; padding: 6px 10px; color: #64748b; font-family: 'Bahnschrift', sans-serif;
    letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.06);
  }}
  .v-table td {{
    padding: 7px 10px; border-bottom: 1px solid rgba(255,255,255,0.03); color: #cbd5e1;
  }}
  .status-tag {{
    background: rgba(16, 185, 129, 0.15); color: #10b981; padding: 2px 6px; border-radius: 3px;
    font-weight: 700; font-size: 9.5px; text-transform: uppercase;
  }}

  /* Bottom highlight pills */
  .bottom-pills {{
    position: absolute; bottom: 25px; left: 0; right: 0;
    display: flex; justify-content: center; gap: 24px; z-index: 10;
  }}
  .b-pill {{
    background: rgba(18, 22, 30, 0.9); border: 1px solid rgba(0, 164, 239, 0.3); border-radius: 20px;
    padding: 6px 18px; font-size: 12px; color: #e2e8f0; display: flex; align-items: center; gap: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
  }}
  .b-pill strong {{ color: #38bdf8; }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow"></div>
  
  <div class="header">
    <div class="badge">📊 DEEP SEARCH & ANALYTICS</div>
    <div class="title">FULL-PAGE VAULT & ACTIVITY HEATMAP</div>
    <div class="subtitle">Comprehensive encrypted history search, date filtering, and 12-month activity analytics</div>
  </div>

  <div class="vault-frame">
    <div class="win-header">
      <div class="win-dots">
        <div class="win-dot dot-r"></div>
        <div class="win-dot dot-y"></div>
        <div class="win-dot dot-g"></div>
      </div>
      <div class="win-url">
        <span>🔒</span>
        <span>chrome-extension://charitra/pages/vault.html</span>
      </div>
      <div style="width: 30px;"></div>
    </div>

    <div class="vault-content">
      <div class="vault-top-bar">
        <div class="v-title">CHARITRA VAULT ANALYTICS</div>
        <div class="v-search-bar">
          <input class="v-search-input" type="text" value="Filter URL, domain, or title..." readonly />
          <button class="v-btn">📅 DATE FILTER</button>
          <button class="v-btn" style="background:#005a9e;">💾 EXPORT JSON</button>
        </div>
      </div>

      <div class="analytics-grid">
        <div class="chart-card">
          <div class="chart-title">TOP BLOCKED SITES (VISIT FREQUENCY)</div>
          <div class="bar-row">
            <span class="bar-label">x.com</span>
            <div class="bar-track"><div class="bar-fill" style="width: 88%; background: #0078d4;"></div></div>
            <span class="bar-val">42</span>
          </div>
          <div class="bar-row">
            <span class="bar-label">reddit.com</span>
            <div class="bar-track"><div class="bar-fill" style="width: 72%; background: #00a4ef;"></div></div>
            <span class="bar-val">36</span>
          </div>
          <div class="bar-row">
            <span class="bar-label">youtube.com</span>
            <div class="bar-track"><div class="bar-fill" style="width: 55%; background: #107c10;"></div></div>
            <span class="bar-val">28</span>
          </div>
          <div class="bar-row">
            <span class="bar-label">instagram.com</span>
            <div class="bar-track"><div class="bar-fill" style="width: 38%; background: #e3008c;"></div></div>
            <span class="bar-val">19</span>
          </div>
        </div>

        <div class="stats-col">
          <div class="stat-mini">
            <div>
              <div class="stat-lbl">TOTAL VAULT CAPTURES</div>
              <div class="stat-num">128</div>
            </div>
            <div style="font-size:24px;">🔒</div>
          </div>
          <div class="stat-mini">
            <div>
              <div class="stat-lbl">ACTIVE BLOCKED DOMAINS</div>
              <div class="stat-num" style="color: #10b981;">14</div>
            </div>
            <div style="font-size:24px;">🛡️</div>
          </div>
        </div>
      </div>

      <div class="heatmap-card">
        <div class="chart-title">12-MONTH PRIVACY ACTIVITY HEATMAP (GITHUB / METRO STYLE)</div>
        <div class="heatmap-grid">
          <div class="hm-cell c-0"></div><div class="hm-cell c-1"></div><div class="hm-cell c-2"></div><div class="hm-cell c-0"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-1"></div><div class="hm-cell c-2"></div><div class="hm-cell c-0"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-0"></div><div class="hm-cell c-1"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-3"></div><div class="hm-cell c-0"></div><div class="hm-cell c-2"></div><div class="hm-cell c-4"></div><div class="hm-cell c-3"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-3"></div><div class="hm-cell c-2"></div><div class="hm-cell c-4"></div><div class="hm-cell c-3"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-3"></div>
          <div class="hm-cell c-1"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-1"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-1"></div><div class="hm-cell c-0"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div><div class="hm-cell c-4"></div><div class="hm-cell c-2"></div><div class="hm-cell c-3"></div>
        </div>
      </div>

      <table class="v-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Domain</th>
            <th>Page Title</th>
            <th>Encrypted Record</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Today, 16:45</td>
            <td style="color:#38bdf8; font-weight:600;">x.com</td>
            <td>Home / X Notifications</td>
            <td style="font-family:monospace; color:#64748b;">4F7A9B2E810C...</td>
            <td><span class="status-tag">WIPED ✓</span></td>
          </tr>
          <tr>
            <td>Today, 15:20</td>
            <td style="color:#38bdf8; font-weight:600;">reddit.com</td>
            <td>r/privacy - Browsing Protection Guide</td>
            <td style="font-family:monospace; color:#64748b;">9E3C1B7D502F...</td>
            <td><span class="status-tag">WIPED ✓</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="bottom-pills">
    <div class="b-pill">🔍 <strong>Multi-Field Search:</strong> Title, URL & Domain</div>
    <div class="b-pill">📊 <strong>Visual Analytics:</strong> 12-Month Heatmap & Frequency Bars</div>
    <div class="b-pill">💾 <strong>Offline Backup:</strong> Password-Protected JSON Export</div>
  </div>
</body>
</html>"""
    return render_html(html, 'screenshot5_analytics_1280x800.png', 1280, 800)

# ==============================================================================
# SMALL PROMO TILE (440x280)
# ==============================================================================
def gen_small_promo():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
  body {{
    width: 440px; height: 280px;
    background: radial-gradient(circle at 50% 30%, #151e2c 0%, #090a0e 80%);
    color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
    position: relative; overflow: hidden;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border: 1px solid rgba(0, 164, 239, 0.35);
  }}
  .bg-grid {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 20px 20px; pointer-events: none;
  }}
  .bg-glow {{
    position: absolute; top: -30px; left: 50%; transform: translateX(-50%);
    width: 280px; height: 160px;
    background: radial-gradient(ellipse at center, rgba(0, 164, 239, 0.3) 0%, rgba(0, 120, 212, 0.1) 50%, transparent 75%);
    filter: blur(25px); pointer-events: none;
  }}
  .brand-icon {{
    width: 68px; height: 68px; filter: drop-shadow(0 0 16px rgba(0, 164, 239, 0.6));
    margin-bottom: 8px; z-index: 5;
  }}
  .brand-title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 32px; font-weight: 700;
    letter-spacing: 3px; color: #ffffff; text-transform: uppercase; line-height: 1;
    z-index: 5; text-shadow: 0 2px 10px rgba(0,0,0,0.7);
  }}
  .brand-sub {{
    font-family: 'Segoe UI', sans-serif; font-size: 13px; color: #38bdf8; font-weight: 600;
    letter-spacing: 0.5px; margin-top: 4px; z-index: 5; text-transform: uppercase;
  }}
  .pills-row {{
    display: flex; gap: 6px; margin-top: 14px; z-index: 5;
  }}
  .pill {{
    background: rgba(0, 120, 212, 0.18); border: 1px solid rgba(0, 164, 239, 0.4);
    color: #f1f5f9; font-size: 10px; font-weight: 700; padding: 3px 10px;
    border-radius: 12px; letter-spacing: 0.5px; text-transform: uppercase;
  }}
  .footer-bar {{
    position: absolute; bottom: 10px; font-size: 9.5px; color: #64748b;
    letter-spacing: 1px; text-transform: uppercase; z-index: 5;
  }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow"></div>
  
  <img class="brand-icon" src="data:image/png;base64,{ICON_B64}" />
  <div class="brand-title">CHARITRA</div>
  <div class="brand-sub">Private Browsing History Vault</div>

  <div class="pills-row">
    <div class="pill">🔒 AES-256-GCM</div>
    <div class="pill">⚡ 1.5s AUTO-WIPE</div>
    <div class="pill">⊞ METRO UI</div>
  </div>

  <div class="footer-bar">
    Zero-Knowledge Architecture • 100% Client-Side
  </div>
</body>
</html>"""
    path = render_html(html, 'promo_small_440x280.png', 440, 280)
    shutil.copy(path, os.path.join(OUTPUT_DIR, 'icon440x280.png'))
    print("Also copied to icon440x280.png")
    return path

# ==============================================================================
# MARQUEE PROMO TILE (1400x560)
# ==============================================================================
def gen_marquee_promo():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
  body {{
    width: 1400px; height: 560px;
    background: radial-gradient(circle at 35% 25%, #151d2c 0%, #090a0e 75%);
    color: #e2e8f0; font-family: 'Segoe UI', sans-serif;
    position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 80px;
    border: 1px solid rgba(0, 164, 239, 0.35);
  }}
  .bg-grid {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 32px 32px; pointer-events: none;
  }}
  .bg-glow {{
    position: absolute; top: -50px; left: 25%;
    width: 750px; height: 420px;
    background: radial-gradient(ellipse at center, rgba(0, 164, 239, 0.22) 0%, rgba(0, 120, 212, 0.08) 50%, transparent 75%);
    filter: blur(45px); pointer-events: none;
  }}

  /* Left Column */
  .left-col {{
    max-width: 680px; display: flex; flex-direction: column; gap: 14px; z-index: 5;
  }}
  .top-badge-row {{
    display: flex; align-items: center; gap: 12px;
  }}
  .store-badge {{
    background: rgba(0, 120, 212, 0.18); border: 1px solid rgba(0, 164, 239, 0.4);
    color: #38bdf8; font-family: 'Bahnschrift', sans-serif; font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; padding: 4px 14px; border-radius: 20px;
  }}
  .brand-logo-row {{
    display: flex; align-items: center; gap: 16px;
  }}
  .brand-icon {{
    width: 64px; height: 64px; filter: drop-shadow(0 0 16px rgba(0, 164, 239, 0.6));
  }}
  .hero-title {{
    font-family: 'Bahnschrift', 'Segoe UI', sans-serif; font-size: 56px; font-weight: 700;
    letter-spacing: 3px; color: #ffffff; text-transform: uppercase; line-height: 1;
    text-shadow: 0 4px 20px rgba(0,0,0,0.8);
  }}
  .hero-tagline {{
    font-family: 'Bahnschrift', sans-serif; font-size: 22px; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    background: linear-gradient(90deg, #38bdf8, #0078d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .hero-desc {{
    font-size: 15px; line-height: 1.5; color: #94a3b8; max-width: 620px;
  }}
  .bullets-list {{
    display: flex; flex-direction: column; gap: 7px; margin-top: 2px;
  }}
  .bullet-item {{
    display: flex; align-items: center; gap: 10px; font-size: 13.5px; color: #f1f5f9;
  }}
  .b-check {{
    color: #10b981; font-weight: 800; font-size: 15px;
  }}
  .trust-strip {{
    display: flex; gap: 16px; font-size: 11px; color: #64748b; letter-spacing: 1px;
    text-transform: uppercase; margin-top: 6px;
  }}
  .trust-strip span {{ display: flex; align-items: center; gap: 5px; }}

  /* Right Showcase Mockup Card */
  .right-showcase {{
    position: relative; z-index: 5; width: 440px; height: 430px;
    display: flex; align-items: center; justify-content: center;
  }}
  .mockup-card {{
    width: 380px; background: #111214; border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 10px; box-shadow: 0 30px 70px -15px rgba(0,0,0,0.95), 0 0 40px rgba(0, 164, 239, 0.3);
    overflow: hidden; display: flex; flex-direction: column;
  }}
  .win-header {{
    background: #181a1f; border-bottom: 1px solid rgba(255,255,255,0.08); padding: 9px 14px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .win-dots {{ display: flex; gap: 6px; }}
  .win-dot {{ width: 9px; height: 9px; border-radius: 50%; }}
  .dot-r {{ background: #ef4444; }} .dot-y {{ background: #f59e0b; }} .dot-g {{ background: #10b981; }}
  .win-label {{
    font-family: 'Bahnschrift', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #94a3b8; text-transform: uppercase; display: flex; align-items: center; gap: 6px;
  }}
  .win-label img {{ width: 14px; height: 14px; border-radius: 2px; }}

  .m-body {{ padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }}
  .m-status {{
    background: linear-gradient(135deg, rgba(0, 120, 212, 0.18), rgba(0, 164, 239, 0.05));
    border: 1px solid rgba(0, 164, 239, 0.3); border-radius: 6px; padding: 10px 12px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .m-pulse {{ width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; }}
  .m-tiles {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  .m-tile {{
    padding: 10px; border-radius: 4px; display: flex; flex-direction: column; justify-content: space-between; height: 58px;
  }}
  .m-tile-b {{ background: #0078d4; color: white; }}
  .m-tile-c {{ background: #005a9e; color: white; }}
  .m-tile-num {{ font-family: 'Bahnschrift', sans-serif; font-size: 20px; font-weight: 700; line-height: 1; }}
  .m-tile-lbl {{ font-size: 9.5px; text-transform: uppercase; opacity: 0.9; }}

  .m-recent {{
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px; padding: 8px 10px; display: flex; justify-content: space-between; align-items: center;
  }}
  .m-host {{ font-size: 11.5px; font-weight: 600; color: #38bdf8; }}
  .m-time {{ font-size: 10px; color: #10b981; font-weight: 600; }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="bg-glow"></div>

  <div class="left-col">
    <div class="top-badge-row">
      <div class="store-badge">CHROME EXTENSION</div>
      <div class="store-badge" style="border-color: rgba(16, 185, 129, 0.4); color: #10b981; background: rgba(16, 185, 129, 0.1);">PRIVACY & SECURITY</div>
    </div>

    <div class="brand-logo-row">
      <img class="brand-icon" src="data:image/png;base64,{ICON_B64}" />
      <div>
        <div class="hero-title">CHARITRA</div>
        <div class="hero-tagline">YOUR PRIVATE BROWSING HISTORY VAULT</div>
      </div>
    </div>

    <div class="hero-desc">
      Silently removes specific domains from your browser history and seals every visit inside an AES-256-GCM encrypted private vault, dressed in vintage Windows Phone / Nokia Lumia Metro style.
    </div>

    <div class="bullets-list">
      <div class="bullet-item">
        <span class="b-check">✓</span>
        <span><strong>1.5-Second Silent History Wiping:</strong> Automatic interception & periodic 7-day deep sweep.</span>
      </div>
      <div class="bullet-item">
        <span class="b-check">✓</span>
        <span><strong>Military-Grade AES-256-GCM Encryption:</strong> PBKDF2-SHA256 with 310,000 iterations (OWASP).</span>
      </div>
      <div class="bullet-item">
        <span class="b-check">✓</span>
        <span><strong>Authentic Nokia Lumia Metro Aesthetics:</strong> Live tiles, 8 vibrant accent themes & visual heatmap.</span>
      </div>
    </div>

    <div class="trust-strip">
      <span>🔒 100% Client-Side</span>
      <span>•</span>
      <span>🚫 Zero Trackers</span>
      <span>•</span>
      <span>🛡️ Zero Plaintext On Disk</span>
      <span>•</span>
      <span>⚖️ Open Source (GPLv3)</span>
    </div>
  </div>

  <div class="right-showcase">
    <div class="mockup-card">
      <div class="win-header">
        <div class="win-dots">
          <div class="win-dot dot-r"></div>
          <div class="win-dot dot-y"></div>
          <div class="win-dot dot-g"></div>
        </div>
        <div class="win-label">
          <img src="data:image/png;base64,{ICON_B64}" />
          CHARITRA VAULT
        </div>
        <div style="width: 25px;"></div>
      </div>

      <div class="m-body">
        <div class="m-status">
          <div style="display:flex; align-items:center; gap:8px;">
            <div class="m-pulse"></div>
            <div>
              <div style="font-family:'Bahnschrift',sans-serif; font-size:12px; font-weight:700; color:white;">PROTECTION ACTIVE</div>
              <div style="font-size:10px; color:#94a3b8;">14 Domains Intercepted</div>
            </div>
          </div>
          <div style="background:#107c10; color:white; font-size:9.5px; font-weight:700; padding:2px 6px; border-radius:3px;">ON</div>
        </div>

        <div class="m-tiles">
          <div class="m-tile m-tile-b">
            <div class="m-tile-num">14</div>
            <div class="m-tile-lbl">BLOCKED SITES</div>
          </div>
          <div class="m-tile m-tile-c">
            <div class="m-tile-num">128</div>
            <div class="m-tile-lbl">VAULT RECORDS</div>
          </div>
        </div>

        <div class="m-recent">
          <div>
            <div class="m-host">x.com</div>
            <div style="font-size:9.5px; color:#64748b;">/notifications</div>
          </div>
          <div class="m-time">2m ago (Wiped)</div>
        </div>

        <div class="m-recent">
          <div>
            <div class="m-host">reddit.com</div>
            <div style="font-size:9.5px; color:#64748b;">/r/technology</div>
          </div>
          <div class="m-time">14m ago (Wiped)</div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""
    path = render_html(html, 'promo_marquee_1400x560.png', 1400, 560)
    shutil.copy(path, os.path.join(OUTPUT_DIR, 'icon1400x560.png'))
    print("Also copied to icon1400x560.png")
    return path

if __name__ == '__main__':
    print("Starting generation of all Chrome Web Store assets...")
    gen_screenshot_1()
    gen_screenshot_2()
    gen_screenshot_3()
    gen_screenshot_4()
    gen_screenshot_5()
    gen_small_promo()
    gen_marquee_promo()
    print("All 7 assets generated successfully!")
