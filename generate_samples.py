import io
import datetime
from pypdf import PdfWriter
from cryptography import x509 as crypto_x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
from pyhanko.sign.signers import SimpleSigner

# 1. Create a clean PDF using pypdf
writer = PdfWriter()
writer.add_blank_page(width=612, height=792)
buf_unsigned = io.BytesIO()
writer.write(buf_unsigned)
buf_unsigned.seek(0)

# Save sample_unsigned.pdf
with open("sample_unsigned.pdf", "wb") as f:
    f.write(buf_unsigned.getvalue())

# 2. Generate RSA Key & Self-Signed Cert
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
key_pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

subject = issuer = crypto_x509.Name([
    crypto_x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
    crypto_x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Delhi"),
    crypto_x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Digital Signatures Lab"),
    crypto_x509.NameAttribute(NameOID.COMMON_NAME, "Self-Signed Test Certificate"),
])

crypto_cert = (
    crypto_x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(crypto_x509.random_serial_number())
    .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
    .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
    .add_extension(
        crypto_x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False
        ),
        critical=True
    )
    .sign(key, hashes.SHA256())
)
cert_pem = crypto_cert.public_bytes(serialization.Encoding.PEM)

with open("test_key.pem", "wb") as f:
    f.write(key_pem)
with open("test_cert.pem", "wb") as f:
    f.write(cert_pem)

signer = SimpleSigner.load(key_file="test_key.pem", cert_file="test_cert.pem")

out_signed = io.BytesIO()
buf_unsigned.seek(0)
w_inc = IncrementalPdfFileWriter(buf_unsigned)
fields.append_signature_field(
    w_inc,
    sig_field_spec=fields.SigFieldSpec(sig_field_name="Signature1")
)
signers.sign_pdf(
    w_inc,
    signers.PdfSignatureMetadata(field_name="Signature1"),
    signer=signer,
    output=out_signed
)

signed_data = out_signed.getvalue()
with open("sample_signed_selfsigned.pdf", "wb") as f:
    f.write(signed_data)

# 3. Create encrypted PDF
writer_enc = PdfWriter()
writer_enc.add_blank_page(width=612, height=792)
writer_enc.encrypt("demo123")
with open("sample_encrypted_pass_demo123.pdf", "wb") as f:
    writer_enc.write(f)

# 4. Create tampered PDF
# We alter 4 bytes in the signed document stream
tampered = bytearray(signed_data)
# find the stream or xref
tampered[300] = (tampered[300] ^ 0xAA)
with open("sample_tampered.pdf", "wb") as f:
    f.write(tampered)

print("SUCCESS: All 4 test sample PDFs created:")
print(" - sample_unsigned.pdf")
print(" - sample_signed_selfsigned.pdf")
print(" - sample_encrypted_pass_demo123.pdf")
print(" - sample_tampered.pdf")
