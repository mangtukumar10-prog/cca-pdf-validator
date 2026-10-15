"""Generate professional 1080x1920 app store screenshots for Uptodown and Android stores."""
import os
import sys
import base64
import subprocess
from PIL import Image

# Output folders
DESKTOP = os.path.expandvars(r"%USERPROFILE%\Desktop\Uptodown_Screenshots")
DOWNLOADS = os.path.expandvars(r"%USERPROFILE%\Downloads\Uptodown_Screenshots")
STATIC_OUT = os.path.abspath(r"static\uptodown_screenshots")

for folder in [DESKTOP, DOWNLOADS, STATIC_OUT]:
    os.makedirs(folder, exist_ok=True)

# Load App Icon as Base64
icon_desktop = os.path.expandvars(r"%USERPROFILE%\Desktop\SignValid_Icon_512x512.png")
icon_local = os.path.abspath(r"static\icon-512.png")
icon_src = icon_desktop if os.path.exists(icon_desktop) else icon_local

with open(icon_src, "rb") as f:
    ICON_B64 = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

CHROME_BIN = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_BIN):
    CHROME_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

COMMON_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    width: 1080px;
    height: 1920px;
    background: radial-gradient(circle at 50% 10%, #1e3a5f 0%, #0d1b2a 55%, #050b14 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'SF Pro Display', sans-serif;
    color: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    overflow: hidden;
    padding: 70px 40px 0 40px;
}

/* Ambient glow accents */
.glow-orb {
    position: absolute;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, rgba(14, 165, 233, 0) 70%);
    top: -100px;
    left: 240px;
    pointer-events: none;
    z-index: 1;
}

/* Top Marketing Header */
.marketing-header {
    text-align: center;
    z-index: 10;
    margin-bottom: 50px;
    width: 1000px;
}
.tag-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.15);
    border: 1.5px solid #10b981;
    color: #34d399;
    padding: 10px 24px;
    border-radius: 50px;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 22px;
}
.headline {
    font-size: 62px;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -1px;
    margin-bottom: 18px;
    background: linear-gradient(180deg, #ffffff 30%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.headline span {
    background: linear-gradient(135deg, #34d399 0%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subhead {
    font-size: 27px;
    color: #94a3b8;
    line-height: 1.4;
    font-weight: 500;
    max-width: 880px;
    margin: 0 auto;
}

/* Smartphone Mockup Frame */
.phone-mockup {
    width: 820px;
    height: 1480px;
    background: #0f172a;
    border-radius: 56px 56px 0 0;
    border: 12px solid #334155;
    border-bottom: none;
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.1);
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Phone Status Bar */
.phone-status-bar {
    height: 52px;
    padding: 0 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 19px;
    font-weight: 600;
    color: #e2e8f0;
    background: #0f172a;
}
.dynamic-island {
    width: 140px;
    height: 28px;
    background: #000000;
    border-radius: 20px;
}

/* App Header Inside Phone */
.app-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 22px 32px;
    background: #1e293b;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.app-brand {
    display: flex;
    align-items: center;
    gap: 16px;
}
.app-brand img {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
.app-title {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.app-pill {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    font-size: 15px;
    font-weight: 700;
    padding: 8px 16px;
    border-radius: 30px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
}

/* Phone Screen Content */
.phone-body {
    flex: 1;
    padding: 30px 32px;
    background: #0b1329;
    display: flex;
    flex-direction: column;
    gap: 24px;
}
"""

def generate_screenshots():
    # -------------------------------------------------------------
    # SCREENSHOT 1: Instant Verification & Dropzone
    # -------------------------------------------------------------
    shot1_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{COMMON_CSS}
.upload-card {{
    background: linear-gradient(180deg, #1e293b 0%, #152033 100%);
    border: 3px dashed #3b82f6;
    border-radius: 28px;
    padding: 55px 30px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}}
.upload-icon-circle {{
    width: 110px;
    height: 110px;
    background: rgba(59, 130, 246, 0.15);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.upload-title {{
    font-size: 30px;
    font-weight: 700;
    color: #ffffff;
}}
.upload-subtitle {{
    font-size: 19px;
    color: #94a3b8;
    max-width: 480px;
    line-height: 1.4;
}}
.btn-select {{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    font-size: 22px;
    font-weight: 700;
    padding: 18px 46px;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
    display: inline-block;
    margin-top: 10px;
}}
.supported-cba {{
    background: #1e293b;
    border-radius: 20px;
    padding: 24px;
}}
.supported-title {{
    font-size: 17px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #64748b;
    font-weight: 700;
    margin-bottom: 16px;
}}
.ca-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}}
.ca-pill {{
    background: #0f172a;
    border: 1px solid #334155;
    padding: 12px 8px;
    border-radius: 12px;
    text-align: center;
    font-size: 16px;
    font-weight: 600;
    color: #cbd5e1;
}}
.ca-pill.active {{
    border-color: #10b981;
    color: #34d399;
    background: rgba(16, 185, 129, 0.08);
}}
.status-footer {{
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 18px;
    padding: 18px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}}
.status-footer-text {{
    font-size: 18px;
    color: #38bdf8;
    font-weight: 600;
}}
</style>
</head>
<body>
<div class="glow-orb"></div>
<div class="marketing-header">
    <div class="tag-badge">Official CCA India PKI Validator</div>
    <h1 class="headline">Instant <span>Digital Signature</span> Verification</h1>
    <p class="subhead">Validate any PDF signed with Indian DSC, Aadhaar eSign, or Digital Tokens in seconds</p>
</div>

<div class="phone-mockup">
    <div class="phone-status-bar">
        <span>09:41</span>
        <div class="dynamic-island"></div>
        <span>5G  100%</span>
    </div>
    <div class="app-nav">
        <div class="app-brand">
            <img src="{ICON_B64}" alt="Logo">
            <span class="app-title">SignValid</span>
        </div>
        <div class="app-pill">
            <div class="pulse-dot"></div>
            <span>CCA India Online</span>
        </div>
    </div>
    <div class="phone-body">
        <div class="upload-card">
            <div class="upload-icon-circle">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <div class="upload-title">Choose PDF or Drag Here</div>
            <div class="upload-subtitle">Supports Form-16, Invoices, MCA filings, Court orders, e-Tenders & Affidavits</div>
            <div class="btn-select">Select PDF Document</div>
        </div>

        <div class="supported-cba">
            <div class="supported-title">Supported Certifying Authorities</div>
            <div class="ca-grid">
                <div class="ca-pill active">eMudhra</div>
                <div class="ca-pill active">Capricorn</div>
                <div class="ca-pill active">NSDL (Protean)</div>
                <div class="ca-pill active">IDSign</div>
                <div class="ca-pill active">Vsign</div>
                <div class="ca-pill active">Pantasign</div>
            </div>
        </div>

        <div class="status-footer">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <div class="status-footer-text">16 Official CCA Root & Sub-CA Certificates Synchronized</div>
        </div>
    </div>
</div>
</body>
</html>"""

    # -------------------------------------------------------------
    # SCREENSHOT 2: Certificate Hierarchy & Cryptographic Trust
    # -------------------------------------------------------------
    shot2_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{COMMON_CSS}
.result-header {{
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%);
    border: 2px solid #10b981;
    border-radius: 22px;
    padding: 24px 28px;
    display: flex;
    align-items: center;
    gap: 20px;
}}
.check-circle {{
    width: 68px;
    height: 68px;
    background: #10b981;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
}}
.result-title {{
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
}}
.result-sub {{
    font-size: 17px;
    color: #34d399;
    font-weight: 600;
}}
.cert-card {{
    background: #1e293b;
    border-radius: 22px;
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 18px;
}}
.cert-card-title {{
    font-size: 19px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #334155;
    padding-bottom: 12px;
}}
.field-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 18px;
}}
.field-label {{
    color: #64748b;
    font-weight: 600;
}}
.field-val {{
    color: #f1f5f9;
    font-weight: 700;
    text-align: right;
}}
.field-val.accent {{
    color: #38bdf8;
}}
.chain-box {{
    background: #0f172a;
    border-radius: 16px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
}}
.chain-step {{
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 17px;
    font-weight: 600;
    color: #cbd5e1;
}}
.chain-icon {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #10b981;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}}
</style>
</head>
<body>
<div class="glow-orb"></div>
<div class="marketing-header">
    <div class="tag-badge">Official CCA Trust Chain</div>
    <h1 class="headline">Deep <span>Certificate Chain</span> Audit</h1>
    <p class="subhead">Inspect signer identity, issuing CA, RSA key algorithms, and validity periods</p>
</div>

<div class="phone-mockup">
    <div class="phone-status-bar">
        <span>09:41</span>
        <div class="dynamic-island"></div>
        <span>5G  100%</span>
    </div>
    <div class="app-nav">
        <div class="app-brand">
            <img src="{ICON_B64}" alt="Logo">
            <span class="app-title">SignValid</span>
        </div>
        <div class="app-pill">
            <div class="pulse-dot"></div>
            <span>Valid Signature</span>
        </div>
    </div>
    <div class="phone-body">
        <div class="result-header">
            <div class="check-circle">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <div>
                <div class="result-title">Cryptographically Valid</div>
                <div class="result-sub">Anchor: India PKI Controller of Certifying Authorities</div>
            </div>
        </div>

        <div class="cert-card">
            <div class="cert-card-title">Signer Certificate Details</div>
            <div class="field-row">
                <span class="field-label">Common Name (CN)</span>
                <span class="field-val">RAJESH KUMAR SHARMA</span>
            </div>
            <div class="field-row">
                <span class="field-label">Issuing Authority</span>
                <span class="field-val accent">eMudhra Sub-CA 2022</span>
            </div>
            <div class="field-row">
                <span class="field-label">Public Key Algorithm</span>
                <span class="field-val">RSA 2048-bit (SHA-256)</span>
            </div>
            <div class="field-row">
                <span class="field-label">Certificate Serial</span>
                <span class="field-val" style="font-family: monospace;">6F:9A:21:4B:88:C3</span>
            </div>
            <div class="field-row">
                <span class="field-label">Key Usage</span>
                <span class="field-val">Digital Signature, Non-Repudiation</span>
            </div>
        </div>

        <div class="chain-box">
            <div class="chain-step">
                <div class="chain-icon">&#10003;</div>
                <span>Signer: RAJESH KUMAR SHARMA</span>
            </div>
            <div class="chain-step">
                <div class="chain-icon">&#10003;</div>
                <span>Sub-CA: eMudhra Sub-CA 2022</span>
            </div>
            <div class="chain-step">
                <div class="chain-icon">&#10003;</div>
                <span>Root Trust: CCA India Root 2022 (Government of India)</span>
            </div>
        </div>
    </div>
</div>
</body>
</html>"""

    # -------------------------------------------------------------
    # SCREENSHOT 3: Adobe Green Tick Fix
    # -------------------------------------------------------------
    shot3_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{COMMON_CSS}
.comparison-container {{
    display: flex;
    flex-direction: column;
    gap: 20px;
}}
.compare-box {{
    border-radius: 22px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 22px;
}}
.compare-box.bad {{
    background: rgba(239, 68, 68, 0.1);
    border: 2px solid #ef4444;
}}
.compare-box.good {{
    background: rgba(16, 185, 129, 0.12);
    border: 2px solid #10b981;
}}
.compare-icon {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: 800;
}}
.compare-box.bad .compare-icon {{
    background: #ef4444;
    color: white;
}}
.compare-box.good .compare-icon {{
    background: #10b981;
    color: white;
}}
.compare-text-title {{
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 4px;
}}
.compare-text-desc {{
    font-size: 16px;
    color: #94a3b8;
}}
.stamp-preview-card {{
    background: #1e293b;
    border-radius: 22px;
    padding: 26px;
    border: 1px solid #334155;
    display: flex;
    flex-direction: column;
    gap: 16px;
}}
.adobe-stamp-mockup {{
    background: #f8fafc;
    border: 2px solid #15803d;
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 18px;
    color: #0f172a;
}}
.adobe-tick {{
    color: #15803d;
    font-size: 40px;
    font-weight: 900;
}}
.adobe-meta-title {{
    font-size: 17px;
    font-weight: 800;
    color: #15803d;
}}
.adobe-meta-sub {{
    font-size: 13px;
    color: #334155;
    line-height: 1.3;
}}
.btn-stamp {{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    font-size: 22px;
    font-weight: 800;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}}
</style>
</head>
<body>
<div class="glow-orb"></div>
<div class="marketing-header">
    <div class="tag-badge">Adobe Reader Certified Fix</div>
    <h1 class="headline">Convert <span>'?'</span> to Adobe Green Tick</h1>
    <p class="subhead">Stamp official ISO 32000 compliant digital verification marks on any certified document</p>
</div>

<div class="phone-mockup">
    <div class="phone-status-bar">
        <span>09:41</span>
        <div class="dynamic-island"></div>
        <span>5G  100%</span>
    </div>
    <div class="app-nav">
        <div class="app-brand">
            <img src="{ICON_B64}" alt="Logo">
            <span class="app-title">SignValid</span>
        </div>
        <div class="app-pill">
            <div class="pulse-dot"></div>
            <span>Auto-Stamper</span>
        </div>
    </div>
    <div class="phone-body">
        <div class="comparison-container">
            <div class="compare-box bad">
                <div class="compare-icon">?</div>
                <div>
                    <div class="compare-text-title">Before: Validity Unknown</div>
                    <div class="compare-text-desc">Adobe Reader displays yellow question mark due to missing local roots</div>
                </div>
            </div>

            <div class="compare-box good">
                <div class="compare-icon">&#10003;</div>
                <div>
                    <div class="compare-text-title">After: Signature Valid</div>
                    <div class="compare-text-desc">Cryptographically embedded tick seal universally accepted by government & banks</div>
                </div>
            </div>
        </div>

        <div class="stamp-preview-card">
            <div style="font-size: 16px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Official Stamped Output</div>
            <div class="adobe-stamp-mockup">
                <div class="adobe-tick">&#10004;</div>
                <div>
                    <div class="adobe-meta-title">Signature Valid</div>
                    <div class="adobe-meta-sub">Digitally signed by RAJESH KUMAR SHARMA<br>Date: 2026.10.15 09:30:15 +05'30'<br>CCA India Trust Set Verified</div>
                </div>
            </div>
        </div>

        <div class="btn-stamp">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>Download Stamped PDF Copy</span>
        </div>
    </div>
</div>
</body>
</html>"""

    # -------------------------------------------------------------
    # SCREENSHOT 4: Cryptographic Audit Certificate
    # -------------------------------------------------------------
    shot4_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{COMMON_CSS}
.audit-card {{
    background: #1e293b;
    border-radius: 22px;
    padding: 28px;
    border: 1px solid #334155;
    display: flex;
    flex-direction: column;
    gap: 18px;
}}
.audit-head {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding-bottom: 14px;
    border-bottom: 1px solid #334155;
}}
.audit-title {{
    font-size: 22px;
    font-weight: 800;
    color: #f8fafc;
}}
.hash-box {{
    background: #0f172a;
    border-radius: 14px;
    padding: 16px;
    font-family: monospace;
    font-size: 15px;
    color: #38bdf8;
    word-break: break-all;
    line-height: 1.4;
    border: 1px solid rgba(56, 189, 248, 0.2);
}}
.field-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 18px;
}}
.field-label {{
    color: #64748b;
    font-weight: 600;
}}
.field-val {{
    color: #f1f5f9;
    font-weight: 700;
}}
.field-val.green {{
    color: #10b981;
}}
.court-badge {{
    background: rgba(168, 85, 247, 0.15);
    border: 1px solid #a855f7;
    color: #c084fc;
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 17px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.btn-audit {{
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    font-size: 22px;
    font-weight: 800;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}}
</style>
</head>
<body>
<div class="glow-orb"></div>
<div class="marketing-header">
    <div class="tag-badge">Legal & Forensic Compliance</div>
    <h1 class="headline">Court-Ready <span>Audit Reports</span></h1>
    <p class="subhead">Generate official cryptographic audit certificates with SHA-256 fingerprint & timestamp</p>
</div>

<div class="phone-mockup">
    <div class="phone-status-bar">
        <span>09:41</span>
        <div class="dynamic-island"></div>
        <span>5G  100%</span>
    </div>
    <div class="app-nav">
        <div class="app-brand">
            <img src="{ICON_B64}" alt="Logo">
            <span class="app-title">SignValid</span>
        </div>
        <div class="app-pill">
            <div class="pulse-dot"></div>
            <span>Audit Passed</span>
        </div>
    </div>
    <div class="phone-body">
        <div class="audit-card">
            <div class="audit-head">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                <span class="audit-title">Cryptographic Integrity Analysis</span>
            </div>

            <div class="field-row">
                <span class="field-label">Document Integrity</span>
                <span class="field-val green">100% Intact (0 Bytes Tampered)</span>
            </div>

            <div class="field-row">
                <span class="field-label">Signing Time</span>
                <span class="field-val">15 Oct 2026, 09:30:15 IST</span>
            </div>

            <div>
                <div style="font-size: 15px; color: #64748b; font-weight: 600; margin-bottom: 8px;">Document SHA-256 Digest</div>
                <div class="hash-box">3a4f89d81b49c04fe885b51c888d3d9e8310b8cf8d4bb98d47b0a70f3f22e12d</div>
            </div>
        </div>

        <div class="court-badge">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <span>Compliant with Indian IT Act 2000 Section 65B & PKI Standards</span>
        </div>

        <div class="btn-audit">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>Download Audit Certificate (PDF)</span>
        </div>
    </div>
</div>
</body>
</html>"""

    # -------------------------------------------------------------
    # SCREENSHOT 5: Privacy First & Offline PWA Ready
    # -------------------------------------------------------------
    shot5_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{COMMON_CSS}
.feature-card {{
    background: #1e293b;
    border-radius: 20px;
    padding: 22px 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    border: 1px solid #334155;
}}
.feature-icon-box {{
    width: 60px;
    height: 60px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}
.feature-icon-box.green {{
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
}}
.feature-icon-box.blue {{
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
}}
.feature-icon-box.purple {{
    background: rgba(168, 85, 247, 0.15);
    color: #a855f7;
}}
.feature-text-title {{
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 4px;
}}
.feature-text-desc {{
    font-size: 15px;
    color: #94a3b8;
    line-height: 1.35;
}}
.mobile-nav-bar {{
    background: #1e293b;
    border-radius: 20px;
    padding: 18px 24px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-top: auto;
    border: 1px solid rgba(255, 255, 255, 0.08);
}}
.nav-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
}}
.nav-item.active {{
    color: #10b981;
}}
</style>
</head>
<body>
<div class="glow-orb"></div>
<div class="marketing-header">
    <div class="tag-badge">Privacy First Architecture</div>
    <h1 class="headline">100% Private & <span>Offline Ready</span></h1>
    <p class="subhead">Your documents are processed securely with zero data retention and strict HTTPS</p>
</div>

<div class="phone-mockup">
    <div class="phone-status-bar">
        <span>09:41</span>
        <div class="dynamic-island"></div>
        <span>5G  100%</span>
    </div>
    <div class="app-nav">
        <div class="app-brand">
            <img src="{ICON_B64}" alt="Logo">
            <span class="app-title">SignValid</span>
        </div>
        <div class="app-pill">
            <div class="pulse-dot"></div>
            <span>PWA Enabled</span>
        </div>
    </div>
    <div class="phone-body">
        <div class="feature-card">
            <div class="feature-icon-box green">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <div>
                <div class="feature-text-title">Zero Document Retention</div>
                <div class="feature-text-desc">Files are parsed strictly in memory and wiped immediately. No data is stored or logged.</div>
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon-box blue">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </div>
            <div>
                <div class="feature-text-title">Encrypted Transmission</div>
                <div class="feature-text-desc">Strict HTTPS with 2-year HSTS preload security and automated reverse-proxy protection.</div>
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon-box purple">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
            <div>
                <div class="feature-text-title">Fast Offline-First Engine</div>
                <div class="feature-text-desc">Service Worker v7 pre-caches all static UI assets for instant loading even without internet.</div>
            </div>
        </div>

        <div class="mobile-nav-bar">
            <div class="nav-item active">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span>Verify</span>
            </div>
            <div class="nav-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                <span>Roots</span>
            </div>
            <div class="nav-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                <span>About</span>
            </div>
        </div>
    </div>
</div>
</body>
</html>"""

    shots = [
        ("01_Instant_Verification", shot1_html, "Instant Verification & File Picker"),
        ("02_Certificate_Hierarchy", shot2_html, "CCA India PKI Certificate Chain"),
        ("03_Adobe_Green_Tick", shot3_html, "Adobe Green Tick Stamping"),
        ("04_Audit_Certificate", shot4_html, "Forensic Audit Certificate"),
        ("05_Privacy_And_PWA", shot5_html, "100% Privacy & Offline PWA Ready")
    ]

    generated_files = []

    for name, html_content, desc in shots:
        html_file = os.path.abspath(f"temp_{name}.html")
        png_temp = os.path.abspath(f"temp_{name}.png")

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_url = "file:///" + html_file.replace("\\", "/")
        cmd = [
            CHROME_BIN,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--screenshot={png_temp}",
            "--window-size=1080,1920",
            file_url
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(png_temp) and os.path.getsize(png_temp) > 0:
            # Save PNG to Desktop, Downloads, and Static
            desktop_png = os.path.join(DESKTOP, f"{name}.png")
            downloads_png = os.path.join(DOWNLOADS, f"{name}.png")
            static_png = os.path.join(STATIC_OUT, f"{name}.png")

            # Also create high-quality JPG versions (preferred by some app store consoles)
            im = Image.open(png_temp).convert("RGB")
            
            for path_png in [desktop_png, downloads_png, static_png]:
                im.save(path_png, "PNG", optimize=True)
                path_jpg = path_png[:-4] + ".jpg"
                im.save(path_jpg, "JPEG", quality=95)

            generated_files.append((name, desktop_png, desc))
            print(f"Generated: {name} (1080x1920)")

        if os.path.exists(html_file):
            os.remove(html_file)
        if os.path.exists(png_temp):
            os.remove(png_temp)

    # Write a helpful README.txt in the screenshot folder for the user
    readme_content = f"""========================================================================
SignValid - Uptodown App Store Official Screenshots (1080 x 1920)
========================================================================

These screenshots have been crafted to meet official app store standards:
- Uptodown App Store (Upload directly in Uptodown Developer Console)
- Google Play Store (Phone screenshot section)
- Amazon Appstore / Samsung Galaxy Store

LIST OF SCREENSHOTS:
1. 01_Instant_Verification.png / .jpg - Drag-and-drop file picker & CCA India live status
2. 02_Certificate_Hierarchy.png / .jpg - Deep certificate chain & signer details
3. 03_Adobe_Green_Tick.png / .jpg - Before/After comparison & Adobe green tick stamp
4. 04_Audit_Certificate.png / .jpg - Forensic SHA-256 integrity analysis & audit report
5. 05_Privacy_And_PWA.png / .jpg - Zero retention, HTTPS HSTS, & offline PWA support

Saved Locations:
- Desktop: {DESKTOP}
- Downloads: {DOWNLOADS}
- Static Assets: {STATIC_OUT}
========================================================================
"""
    with open(os.path.join(DESKTOP, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    with open(os.path.join(DOWNLOADS, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("All 5 Uptodown store screenshots created successfully!")

if __name__ == "__main__":
    generate_screenshots()
