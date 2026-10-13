"""FastAPI Web Server for CCA India PDF Signature Validator."""
import os
import asyncio
import shutil
import glob
import hashlib
import re
import urllib.parse
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

from validator import global_store, validate_pdf_data, parse_cert_info, ROOTS_DIR
import sync_cca_roots
import pdf_stamper

# Cache recently validated files for immediate 1-click download of verified copy or audit certificate
recent_validated_files: Dict[str, Dict[str, Any]] = {}

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(HERE, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(ROOTS_DIR, exist_ok=True)

app = FastAPI(
    title="CCA India PDF Signature Validator",
    description="Validate PDF Digital Signatures against the official Controller of Certifying Authorities (CCA) India PKI Trust Set",
    version="2.0.0"
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom StaticFiles class to set long-term cache headers for assets
class CachedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            # 7 days browser cache for images, icons, and static assets
            response.headers["Cache-Control"] = "public, max-age=604800, immutable"
        return response

# Mount static folder with caching
app.mount("/static", CachedStaticFiles(directory=STATIC_DIR), name="static")

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" fill="#116d44"/><path d="M25 50 L42 67 L75 33" stroke="white" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>"""

@app.get("/sw.js", include_in_schema=False)
async def serve_service_worker():
    sw_file = os.path.join(STATIC_DIR, "sw.js")
    if os.path.exists(sw_file):
        with open(sw_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})
    return Response(content="", media_type="application/javascript")

@app.get("/.well-known/assetlinks.json", include_in_schema=False)
@app.get("/static/.well-known/assetlinks.json", include_in_schema=False)
async def serve_assetlinks():
    al_file = os.path.join(STATIC_DIR, ".well-known", "assetlinks.json")
    if os.path.exists(al_file):
        with open(al_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/json")
    return Response(content="[]", media_type="application/json")

@app.get("/manifest.json", include_in_schema=False)
@app.get("/static/manifest.json", include_in_schema=False)
async def serve_manifest():
    m_file = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(m_file):
        with open(m_file, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="application/manifest+json")
    return Response(content="{}", media_type="application/manifest+json")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")

@app.get("/ads.txt", response_class=Response, include_in_schema=False)
async def serve_ads_txt():
    ads_txt_file = os.path.join(STATIC_DIR, "ads.txt")
    if os.path.exists(ads_txt_file):
        with open(ads_txt_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n"
    return Response(content=content, media_type="text/plain")

@app.get("/google{code}.html", response_class=HTMLResponse, include_in_schema=False)
async def serve_google_verification(code: str):
    filename = f"google{code}.html"
    file_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"google-site-verification: google{code}.html")

@app.get("/robots.txt", response_class=Response, include_in_schema=False)
async def serve_robots_txt():
    path = os.path.join(STATIC_DIR, "robots.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "User-agent: *\nAllow: /\nSitemap: https://cca-pdf-validator.onrender.com/sitemap.xml\n"
    return Response(content=content, media_type="text/plain")

@app.get("/sitemap.xml", response_class=Response, include_in_schema=False)
async def serve_sitemap_xml():
    path = os.path.join(STATIC_DIR, "sitemap.xml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://cca-pdf-validator.onrender.com/</loc></url></urlset>'
    return Response(content=content, media_type="application/xml")

@app.get("/api/adsense")
async def get_adsense_info():
    ads_txt_file = os.path.join(STATIC_DIR, "ads.txt")
    pub_id = "pub-0000000000000000"
    if os.path.exists(ads_txt_file):
        with open(ads_txt_file, "r", encoding="utf-8") as f:
            for line in f:
                if "google.com" in line and "DIRECT" in line:
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 2:
                        pub_id = parts[1]
                        break
    return {
        "status": "ready",
        "publisher_id": pub_id,
        "ads_txt_url": "/ads.txt",
        "slots": ["cca_header_banner", "cca_mid_results", "cca_footer_banner"]
    }

@app.post("/api/adsense/save")
async def save_adsense_pub(pub_id: str = Form(...)):
    clean_id = pub_id.strip()
    if clean_id:
        clean_pub = clean_id.replace("ca-", "")
        ads_txt_file = os.path.join(STATIC_DIR, "ads.txt")
        with open(ads_txt_file, "w", encoding="utf-8") as f:
            f.write(f"google.com, {clean_pub}, DIRECT, f08c47fec0942fa0\n")
        return {"success": True, "pub_id": clean_id, "ads_txt": f"google.com, {clean_pub}, DIRECT, f08c47fec0942fa0"}
    raise HTTPException(status_code=400, detail="Invalid Publisher ID")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(
            content=content,
            headers={
                "Cache-Control": "public, max-age=300, s-maxage=600, stale-while-revalidate=86400",
                "X-Robots-Tag": "index, follow"
            }
        )
    return "<h1>CCA India PDF Signature Validator</h1><p>Static index.html not found.</p>"

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "roots_loaded": len(global_store.certs),
        "roots_metadata_count": len(global_store.cert_metadata)
    }

@app.get("/api/roots")
async def get_roots():
    return {
        "total": len(global_store.cert_metadata),
        "certificates": global_store.cert_metadata
    }

@app.post("/api/roots/reload")
async def reload_roots():
    global_store.reload()
    return {
        "success": True,
        "message": f"Successfully loaded {len(global_store.certs)} certificates into trust store.",
        "total": len(global_store.certs)
    }

@app.post("/api/roots/sync")
async def sync_roots_from_cca():
    try:
        sync_cca_roots.sync()
        global_store.reload()
        return {
            "success": True,
            "message": f"Sync completed. Trust store updated with {len(global_store.certs)} certificates.",
            "total": len(global_store.certs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/roots/upload")
async def upload_root_certs(files: List[UploadFile] = File(...)):
    saved = []
    for file in files:
        if not file.filename:
            continue
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".cer", ".crt", ".pem", ".der"]:
            continue
        dest = os.path.join(ROOTS_DIR, file.filename)
        content = await file.read()
        with open(dest, "wb") as f:
            f.write(content)
        saved.append(file.filename)
    
    global_store.reload()
    return {
        "success": True,
        "saved_files": saved,
        "total_roots_now": len(global_store.certs)
    }

@app.post("/api/validate")
async def validate_pdfs(
    files: List[UploadFile] = File(...),
    password: Optional[str] = Form(None),
    offline: bool = Form(True),
    trust_system: bool = Form(False)
):
    results = []
    clean_pw = password.strip() if password else None
    for file in files:
        content = await file.read()
        fname = file.filename or "uploaded.pdf"
        res = await asyncio.to_thread(
            validate_pdf_data,
            pdf_bytes=content,
            filename=fname,
            password=clean_pw,
            offline=offline,
            trust_system=trust_system
        )
        if res.get("sha256"):
            if len(recent_validated_files) > 100:
                oldest_k = next(iter(recent_validated_files))
                recent_validated_files.pop(oldest_k, None)
            recent_validated_files[res["sha256"]] = {
                "bytes": content,
                "res": res,
                "filename": fname
            }
        results.append(res)
    return results

def get_validated_file_data(sha256: str) -> Optional[Dict[str, Any]]:
    sha256_clean = sha256.lower().strip()
    for k, v in recent_validated_files.items():
        if k.lower().strip() == sha256_clean:
            return v
    
    # Disk lookup fallback across workspace and downloads
    search_dirs = [HERE, r"C:\Users\mangtu\Downloads"]
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        for p in glob.glob(os.path.join(s_dir, "*.pdf")):
            try:
                with open(p, "rb") as fh:
                    content = fh.read()
                if hashlib.sha256(content).hexdigest().lower() == sha256_clean:
                    res = validate_pdf_data(content, os.path.basename(p))
                    entry = {"bytes": content, "res": res, "filename": os.path.basename(p)}
                    recent_validated_files[res["sha256"]] = entry
                    return entry
            except Exception:
                pass
    return None

@app.get("/api/download-verified/{sha256}")
async def download_verified_by_hash(sha256: str):
    data = get_validated_file_data(sha256)
    if not data:
        raise HTTPException(status_code=404, detail="File validation session expired or not found")
    verified_bytes = pdf_stamper.generate_verified_display_pdf(data["bytes"], data["res"])
    base_name = os.path.splitext(data["filename"])[0]
    safe_base = re.sub(r'[^\w\-\.]', '_', base_name)
    encoded_name = urllib.parse.quote(f"{base_name}_verified.pdf")
    return Response(
        content=verified_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_base}_verified.pdf"; filename*=UTF-8\'\'{encoded_name}'}
    )

@app.get("/api/download-audit-cert/{sha256}")
async def download_audit_cert_by_hash(sha256: str):
    data = get_validated_file_data(sha256)
    if not data:
        raise HTTPException(status_code=404, detail="File validation session expired or not found")
    cert_bytes = pdf_stamper.generate_audit_certificate_pdf(data["res"])
    base_name = os.path.splitext(data["filename"])[0]
    safe_base = re.sub(r'[^\w\-\.]', '_', base_name)
    encoded_name = urllib.parse.quote(f"Audit_Certificate_{base_name}.pdf")
    return Response(
        content=cert_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Audit_Certificate_{safe_base}.pdf"; filename*=UTF-8\'\'{encoded_name}'}
    )

@app.get("/api/samples")
async def list_samples():
    sample_names = [
        {"id": "birthcert", "filename": "sample_rajasthan_birth_certificate_signed.pdf", "title": "Rajasthan Birth Certificate (Pehchan Portal)", "description": "Genuine digital signature issued by Rajasthan Gov & SpeedSign, chained to CCA India 2022."},
        {"id": "selfsigned", "filename": "sample_signed_selfsigned.pdf", "title": "Self-Signed Test PDF", "description": "Cryptographically intact & valid math, but untrusted root."},
        {"id": "unsigned", "filename": "sample_unsigned.pdf", "title": "Unsigned Standard PDF", "description": "Clean PDF without digital signatures."},
        {"id": "encrypted", "filename": "sample_encrypted_pass_demo123.pdf", "title": "Encrypted PDF (Password: demo123)", "description": "Password-protected document testing decryption."},
        {"id": "tampered", "filename": "sample_tampered.pdf", "title": "Tampered / Altered PDF", "description": "Signed document whose bytes were altered post-signing."}
    ]
    available = []
    for s in sample_names:
        p = os.path.join(HERE, s["filename"])
        if os.path.exists(p):
            available.append(s)
    return available

@app.get("/api/samples/{filename}")
async def get_sample_file(filename: str):
    p = os.path.join(HERE, filename)
    if not os.path.exists(p):
        raise HTTPException(status_code=404, detail="Sample not found")
    return FileResponse(p, filename=filename, media_type="application/pdf")

@app.post("/api/samples/{filename}/validate")
async def validate_sample_file(
    filename: str,
    password: Optional[str] = Form(None),
    offline: bool = Form(True)
):
    p = os.path.join(HERE, filename)
    if not os.path.exists(p):
        raise HTTPException(status_code=404, detail="Sample not found")
    with open(p, "rb") as f:
        content = f.read()
    if "encrypted" in filename and not password:
        password = "demo123"
    res = await asyncio.to_thread(
        validate_pdf_data,
        pdf_bytes=content,
        filename=filename,
        password=password,
        offline=offline,
        trust_system=False
    )
    if res.get("sha256"):
        recent_validated_files[res["sha256"]] = {
            "bytes": content,
            "res": res,
            "filename": filename
        }
    return [res]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
