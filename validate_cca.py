#!/usr/bin/env python3
"""Validate PDF signatures against the CCA India trust set (needs network for revocation checks).

Usage:  python validate_cca.py file1.pdf file2.pdf [--password PW] [--offline]
Put the CCA root + intermediate certificates (.cer/.crt/.pem/.der) in ./roots
"""
import argparse, json, os, sys
from validator import validate_pdf_data, global_store

def check(path, password, offline):
    if not os.path.exists(path):
        return {"file": os.path.basename(path), "error": "File not found"}
    with open(path, "rb") as fh:
        pdf_bytes = fh.read()
    return validate_pdf_data(
        pdf_bytes=pdf_bytes,
        filename=os.path.basename(path),
        password=password,
        offline=offline,
        trust_system=False
    )

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--password")
    ap.add_argument("--offline", action="store_true", help="skip OCSP/CRL fetching")
    a = ap.parse_args()
    if not global_store.certs:
        sys.exit("No certificates in ./roots - download the CCA India roots first (see README).")
    print(json.dumps([check(p, a.password, a.offline) for p in a.pdfs], indent=2))
