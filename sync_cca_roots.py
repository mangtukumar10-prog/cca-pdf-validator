"""Sync CCA India Root and Intermediate Certificates from official portal https://cca.gov.in"""
import urllib.request
import re
import os
import base64
import urllib.parse
from asn1crypto import x509

HERE = os.path.dirname(os.path.abspath(__file__))
ROOTS_DIR = os.path.join(HERE, "roots")
os.makedirs(ROOTS_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

PAGES = [
    'https://cca.gov.in/root_certificate.html',
    'https://cca.gov.in/root_ca_india.html',
    'https://cca.gov.in/display_cert2022.php',
    'https://cca.gov.in/display_cert2022_SPL.php',
    'https://cca.gov.in/display_cert2015.php',
    'https://cca.gov.in/display_cert2014.php',
    'https://cca.gov.in/display_cert2011.php',
    'https://cca.gov.in/display_cert2007.php'
]

def sync():
    found_urls = set()
    for page in PAGES:
        try:
            req = urllib.request.Request(page, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
            for m in re.finditer(r'href=["\']([^"\']+\.(?:cer|crt|pem|der))["\']', html, re.I):
                full_url = urllib.parse.urljoin(page, m.group(1))
                found_urls.add(full_url)
        except Exception as e:
            print(f"Error reading {page}: {e}")

    print(f"Discovered {len(found_urls)} certificates from CCA India.")
    downloaded = 0
    for url in sorted(found_urls):
        raw_name = os.path.basename(url.split('?')[0])
        clean_name = urllib.parse.unquote(raw_name)
        target = os.path.join(ROOTS_DIR, clean_name)
        if not os.path.exists(target):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                # Normalize base64 if needed
                stripped = data.strip()
                if b'BEGIN CERTIFICATE' not in stripped and not stripped.startswith(b'\x30'):
                    try:
                        data = base64.b64decode(stripped)
                    except Exception:
                        pass
                with open(target, 'wb') as f:
                    f.write(data)
                downloaded += 1
                print(f"Downloaded: {clean_name}")
            except Exception as e:
                print(f"Failed {url}: {e}")
    print(f"Sync complete. Downloaded {downloaded} new certificates. Total in roots: {len(os.listdir(ROOTS_DIR))}")

if __name__ == "__main__":
    sync()
