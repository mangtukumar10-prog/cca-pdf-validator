import glob
import os
import json
import traceback
from validator import validate_pdf_data

pdf_files = glob.glob(r"C:\Users\mangtu\Downloads\*.pdf")
print(f"Testing {len(pdf_files)} PDFs in Downloads:")

for p in pdf_files:
    fname = os.path.basename(p)
    try:
        with open(p, "rb") as f:
            b = f.read()
        res = validate_pdf_data(b, fname)
        verdict = res.get("verdict")
        sigs_count = len(res.get("signatures", []))
        print(f"OK: {fname[:38]:<40} | verdict: {verdict:<20} | sigs: {sigs_count}")
        if res.get("signatures"):
            for s in res["signatures"]:
                print(f"     Signer: {s.get('signer_name')} | Intact: {s.get('intact')} | Valid: {s.get('valid')} | Trusted: {s.get('trusted')}")
    except Exception as e:
        print(f"FAILED: {fname} -> {e}")
        traceback.print_exc()
