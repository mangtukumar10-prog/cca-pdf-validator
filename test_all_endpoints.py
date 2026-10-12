import urllib.request
import json
import os

BASE_URL = "http://127.0.0.1:8000"

print("1. Testing homepage...")
r = urllib.request.urlopen(BASE_URL + "/")
assert r.getcode() == 200
print("   Homepage OK:", len(r.read()), "bytes")

print("2. Testing roots endpoint...")
r = urllib.request.urlopen(BASE_URL + "/api/roots")
roots_data = json.loads(r.read())
print(f"   Loaded {roots_data.get('total')} roots OK.")

print("3. Testing sample validation: vivan_birth_certificate_original_signed.pdf...")
req = urllib.request.Request(
    BASE_URL + "/api/samples/vivan_birth_certificate_original_signed.pdf/validate",
    data=b"",
    method="POST"
)
r = urllib.request.urlopen(req)
val_res = json.loads(r.read())[0]
sha = val_res["sha256"]
print(f"   Verdict: {val_res.get('verdict')} | Signer: {val_res['signatures'][0]['signer_name']}")
assert val_res.get("verdict") == "VERIFIED_GENUINE"
assert val_res["signatures"][0]["intact"] is True
assert val_res["signatures"][0]["trusted"] is True

print("4. Testing download verified copy...")
r = urllib.request.urlopen(f"{BASE_URL}/api/download-verified/{sha}")
verified_bytes = r.read()
print(f"   Verified PDF downloaded OK: {len(verified_bytes)} bytes")
assert len(verified_bytes) > 1000

print("5. Testing download audit cert...")
r = urllib.request.urlopen(f"{BASE_URL}/api/download-audit-cert/{sha}")
audit_bytes = r.read()
print(f"   Audit cert downloaded OK: {len(audit_bytes)} bytes")
assert len(audit_bytes) > 1000

print("6. Testing re-validation of the generated verified display copy...")
from validator import validate_pdf_data
reval = validate_pdf_data(verified_bytes, "verified_copy.pdf")
print(f"   Re-validation verdict: {reval.get('verdict')} | Title: {reval.get('verdict_title')}")
assert reval.get("verdict") == "SIGNVALID_DISPLAY_COPY"

print("7. Testing scanned document handling...")
scanned_path = r"C:\Users\mangtu\Downloads\VIVAN BIRTH CERIFICATE.pdf"
if os.path.exists(scanned_path):
    with open(scanned_path, "rb") as f:
        scanned_bytes = f.read()
    scan_res = validate_pdf_data(scanned_bytes, "VIVAN BIRTH CERIFICATE.pdf")
    print(f"   Scanned PDF verdict: {scan_res.get('verdict')} | Title: {scan_res.get('verdict_title')}")
    print(f"   Sample hint provided: {scan_res.get('sample_hint')}")

print("8. Testing /ads.txt endpoint...")
r = urllib.request.urlopen(f"{BASE_URL}/ads.txt")
ads_content = r.read().decode('utf-8')
print("   /ads.txt content:", ads_content.strip())
assert "google.com" in ads_content and "DIRECT" in ads_content

print("9. Testing /api/adsense endpoint...")
r = urllib.request.urlopen(f"{BASE_URL}/api/adsense")
ads_meta = json.loads(r.read())
print(f"   AdSense Publisher ID: {ads_meta.get('publisher_id')} | Status: {ads_meta.get('status')}")
assert ads_meta.get("status") == "ready"

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
