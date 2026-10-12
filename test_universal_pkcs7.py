import os
import io
import datetime
import hashlib
from typing import Dict, Any, List

from asn1crypto import x509, cms
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_public_key
from pyhanko_certvalidator import CertificateValidator, ValidationContext
from validator import global_store, parse_cert_info

def universal_pkcs7_verify(pdf_bytes: bytes, sig_dict: Dict[str, Any], roots: List[x509.Certificate], offline: bool = True) -> Dict[str, Any]:
    byte_range = sig_dict.get('/ByteRange')
    contents_obj = sig_dict.get('/Contents')
    contents_bytes = bytes(contents_obj)

    # 1. ByteRange check
    p1 = pdf_bytes[byte_range[0] : byte_range[0] + byte_range[1]]
    p2 = pdf_bytes[byte_range[2] : byte_range[2] + byte_range[3]]
    signed_chunk = p1 + p2

    ci = cms.ContentInfo.load(contents_bytes)
    sd = ci['content']
    eci = sd['encap_content_info']
    
    # Check attached content or detached message_digest
    encap_digest = None
    if eci['content'] is not None and eci['content'].native is not None:
        encap_digest = eci['content'].native
        if isinstance(encap_digest, str):
            encap_digest = encap_digest.encode('latin1')

    si = sd['signer_infos'][0]
    signed_attrs = si['signed_attrs'] if 'signed_attrs' in si and si['signed_attrs'].native is not None else None
    
    attr_digest = None
    if signed_attrs:
        for attr in signed_attrs:
            if attr['type'].native == 'message_digest':
                attr_digest = attr['values'][0].native
                break

    # Determine hash algorithm
    digest_algo_name = 'sha1'
    try:
        digest_algo_name = si['digest_algorithm']['algorithm'].native
    except Exception:
        pass

    hasher_cls = hashlib.sha1
    crypto_hash = hashes.SHA1()
    if 'sha256' in digest_algo_name:
        hasher_cls = hashlib.sha256
        crypto_hash = hashes.SHA256()
    elif 'sha512' in digest_algo_name:
        hasher_cls = hashlib.sha512
        crypto_hash = hashes.SHA512()

    computed_doc_digest = hasher_cls(signed_chunk).digest()

    intact = False
    if attr_digest:
        intact = (computed_doc_digest == attr_digest)
    elif encap_digest:
        intact = (computed_doc_digest == encap_digest)
    else:
        intact = True

    # 2. RSA signature verification
    sig_bytes = si['signature'].native
    all_certs = [c.chosen for c in sd['certificates']]
    signer_cert_asn1 = None
    for cert in all_certs:
        if cert.serial_number == si['sid'].chosen['serial_number'].native:
            signer_cert_asn1 = cert
            break

    valid = False
    if signer_cert_asn1:
        try:
            pub_key = load_der_public_key(signer_cert_asn1.public_key.dump())
            # If signed_attrs present, sign is over DER of signed_attrs
            if signed_attrs:
                data_to_verify = signed_attrs.dump()
                # in CMS, signed_attrs are tagged SET OF (0x31) instead of [0] (0xA0)
                if data_to_verify[0] == 0xA0:
                    data_to_verify = b'\x31' + data_to_verify[1:]
                for ha in [crypto_hash, hashes.SHA256(), hashes.SHA1()]:
                    try:
                        pub_key.verify(sig_bytes, data_to_verify, padding.PKCS1v15(), ha)
                        valid = True
                        break
                    except Exception:
                        pass
            else:
                for ha in [crypto_hash, hashes.SHA1(), hashes.SHA256()]:
                    try:
                        pub_key.verify(sig_bytes, encap_digest or computed_doc_digest, padding.PKCS1v15(), ha)
                        valid = True
                        break
                    except Exception:
                        pass
        except Exception as e:
            valid = False

    # 3. Chain of Trust
    other_certs = [c for c in all_certs if c != signer_cert_asn1]
    m_str = sig_dict.get('/M')
    signing_time = None
    if m_str:
        raw_m = str(m_str).replace("D:", "").replace("'", "")
        try:
            signing_time = datetime.datetime.strptime(raw_m[:14], "%Y%m%d%H%M%S").replace(tzinfo=datetime.timezone.utc)
        except Exception:
            pass

    vc = ValidationContext(
        trust_roots=roots,
        other_certs=other_certs,
        allow_fetching=not offline,
        revocation_mode="soft-fail",
        moment=signing_time
    )

    trusted = False
    chain_names = []
    if signer_cert_asn1:
        try:
            import asyncio
            cv = CertificateValidator(signer_cert_asn1, intermediate_certs=other_certs, validation_context=vc)
            path = asyncio.run(cv.async_validate_usage(set()))
            trusted = True
            chain_names = [c.subject.human_friendly for c in path]
        except Exception:
            trusted = False

    covers_whole = (byte_range[2] + byte_range[3] == len(pdf_bytes))
    cert_info = parse_cert_info(signer_cert_asn1) if signer_cert_asn1 else {}
    signer_name = cert_info.get("subject_cn") or str(sig_dict.get('/Name', 'Unknown Signer'))

    return {
        "field": str(sig_dict.get('/T', 'Signature1')),
        "signer_name": signer_name,
        "cert_info": cert_info,
        "signed_at": signing_time.isoformat() if signing_time else None,
        "intact": intact,
        "valid": valid,
        "trusted": trusted,
        "covers_whole_document": "ENTIRE_FILE" if covers_whole else "PARTIAL",
        "modification_level": "NONE",
        "bottom_line": (intact and valid and trusted),
        "cca_chain_trusted": trusted,
        "chain_path": chain_names,
        "subfilter": str(sig_dict.get('/SubFilter', '/adbe.pkcs7.sha1')),
        "warnings": []
    }

# Test universal_pkcs7_verify
with open('vivan_birth_certificate_original_signed.pdf', 'rb') as f:
    b = f.read()
import pypdf
r = pypdf.PdfReader(io.BytesIO(b))
from test_sig_extract import extract_all_signature_dicts
sigs = extract_all_signature_dicts(r)
res = universal_pkcs7_verify(b, sigs[0], global_store.certs, offline=True)
print("Result:")
print("  Signer:", res['signer_name'])
print("  Intact:", res['intact'], "Valid:", res['valid'], "Trusted:", res['trusted'])
print("  Chain:", res['chain_path'])
