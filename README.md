# CCA India PDF Signature Validator

A full-featured web application and command-line tool for verifying PDF digital signatures against the official **Controller of Certifying Authorities (CCA)** India Public Key Infrastructure (PKI) trust set (under Section 35 of the Information Technology Act 2000).

Includes 62 pre-bundled and normalized official CCA India Root Certificates (CCA India 2022, 2022 SPL, 2015, 2014, 2011, 2007) and licensed Certifying Authorities' intermediate certificates (e-Mudhra, Capricorn, (n)Code, C-DAC, Protean/NSDL, IDRBT, SafeScrypt, CDSL, RajComp, VSign, PantaSign, etc.).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Web Site
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Then open your browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

*(Interactive Swagger API docs are also available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs))*

---

## 💻 CLI Usage

You can also run the original command-line validator tool directly:

```bash
# Validate one or multiple PDFs
python validate_cca.py document.pdf

# Validate password-protected e-Aadhaar
python validate_cca.py eaadhaar.pdf --password "<FIRST4LETTERS_CAPS><YEAR>"

# Fast offline validation (skips live OCSP/CRL network queries)
python validate_cca.py my_invoice.pdf --offline
```

---

## 🌟 Web Site Features

1. **Drag & Drop Upload:**
   - Multi-file batch verification for e-Aadhaar, DigiLocker docs, Form 16, invoices, and legal PDFs.
2. **e-Aadhaar & Password Support:**
   - Built-in password input with visibility toggle. Auto-detects encryption.
3. **Triple Verification Standard:**
   - 🛡️ **Chain of Trust:** Verifies cryptographic anchor up to the official CCA India Root CA.
   - 🔒 **Cryptographic Validity:** Mathematical check of the RSA/ECDSA signature digest.
   - 📄 **Document Integrity:** Byte-range hash verification ensuring document is unaltered since signing.
4. **Certificate Deep-Dive Inspector:**
   - Parses signer Common Name (CN), Organization (O), Unit (OU), State, and Country.
   - Displays Certificate Serial Number, Issuer CA, Validity Window, SHA256 Fingerprint, and Key Algorithm/Size.
5. **Trust Store Manager:**
   - Live searchable explorer of all 62 active CCA root and intermediate certificates.
   - One-click certificate upload (`.cer`, `.crt`, `.pem`, `.der`).
   - Sync updater button fetching updates directly from `cca.gov.in`.
6. **Quick Test Presets:**
   - 🧪 Self-signed sample (Tests valid math + untrusted root warning)
   - 📄 Unsigned sample (Tests signature detection)
   - 🔐 Encrypted sample (Tests password handling)
   - ⚠️ Tampered sample (Tests document modification detection)
7. **Instant Downloads & Export:**
   - 📥 **Download Verified PDF (with Green Tick):** Overlays an official green tick verification stamp (`✔ Signature Valid`) and top verification ribbon directly onto the document.
   - 📜 **Download Audit Certificate (PDF):** Generates an official 1-page Cryptographic Verification Audit Certificate recognized under Section 35 of the IT Act 2000.
   - 📄 **Download Raw JSON Report:** Full structured cryptographic report for auditing and record-keeping.

---

## 📁 Repository Structure

```text
├── main.py              # FastAPI web server and REST API endpoints
├── validator.py         # Core signature validation and certificate store engine
├── validate_cca.py      # Standalone CLI validation script
├── sync_cca_roots.py    # Direct certificate synchronizer from cca.gov.in
├── generate_samples.py  # Test sample PDFs generator
├── roots/               # 62 official CCA root & intermediate certificates (.cer)
├── static/
│   └── index.html       # Responsive Tailwind CSS & Lucide Single-Page App
├── requirements.txt     # Python package requirements
└── README.md            # Documentation and instructions
```

---

## 📡 REST API Reference

- `POST /api/validate`: Upload PDFs (`multipart/form-data`) with optional `password`, `offline`, and `trust_system` parameters.
- `GET /api/roots`: Returns metadata of all 62 loaded root & intermediate certificates.
- `POST /api/roots/upload`: Upload additional `.cer` / `.crt` / `.pem` certificates dynamically.
- `POST /api/roots/sync`: Pull latest certificates directly from `cca.gov.in`.
- `GET /api/samples`: List available sample test PDFs.
- `POST /api/samples/{filename}/validate`: Instant server-side sample validation.
- `GET /api/health`: Health status and count of active trust anchors.
