import io
import pypdf
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image

def create_exact_adobe_stamp_overlay(pw, ph, sig_rect=None, signer="AMIT GARG", date_str="2026.01.03 16:05:08 +05:30"):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(pw, ph))

    # Standard location in Rajasthan Pehchan certificate: Rect [450, 158, 500, 208]
    if sig_rect and len(sig_rect) == 4:
        x1, y1, x2, y2 = sig_rect
        bx = min(x1, x2)
        by = min(y1, y2)
        bw = abs(x2 - x1)
        bh = abs(y2 - y1)
    else:
        bx, by, bw, bh = 450, 158, 50, 50

    cx = bx + bw / 2.0
    cy = by + bh / 2.0

    cw = 32.0
    ch = 32.0 * (133.0 / 132.0)
    ck_x = cx - cw * 0.10
    ck_y = cy - ch * 0.50

    # 1. "Signature valid" in Times-Roman (Serif)
    can.setFont("Times-Roman", 12.0)
    can.setFillColor(colors.HexColor("#000000"))
    can.drawCentredString(cx - 2, ck_y + ch + 7, "Signature valid")

    # 2. Polygon points for green checkmark (PDF coords, 0 to 1)
    pts = [
        (0.000, 0.391),  # 1. Left tip
        (0.068, 0.474),  # 2. Left top
        (0.311, 0.128),  # 3. Inner valley
        (0.864, 1.000),  # 4. Top right tip
        (1.000, 0.902),  # 5. Far right corner
        (0.348, 0.000),  # 6. Bottom vertex
    ]

    def to_c(nx, ny, ox=0, oy=0):
        return (ck_x + nx * cw + ox, ck_y + ny * ch + oy)

    # 3D Black Drop Shadow
    sh_x = 1.3
    sh_y = -1.3
    can.setFillColor(colors.HexColor("#000000"))
    p_sh = can.beginPath()
    p_sh.moveTo(*to_c(*pts[0], sh_x, sh_y))
    for pt in pts[1:]:
        p_sh.lineTo(*to_c(*pt, sh_x, sh_y))
    p_sh.close()
    can.drawPath(p_sh, fill=1, stroke=0)

    # Vivid Green Checkmark (#00962E)
    can.setFillColor(colors.HexColor("#00962E"))
    p_gr = can.beginPath()
    p_gr.moveTo(*to_c(*pts[0]))
    for pt in pts[1:]:
        p_gr.lineTo(*to_c(*pt))
    p_gr.close()
    can.drawPath(p_gr, fill=1, stroke=0)

    # 3. Overlaid Signer Text in Helvetica
    tx = ck_x - 18.0
    ty = ck_y + ch * 0.52
    lh = 8.8

    parts = date_str.split(" ", 1) if " " in date_str else [date_str, ""]
    d_part = parts[0]
    t_part = parts[1] if len(parts) > 1 else ""

    can.setFont("Helvetica", 7.6)
    can.setFillColor(colors.HexColor("#000000"))
    can.drawString(tx, ty, "Digitally signed by")
    can.drawString(tx, ty - lh, signer)
    can.drawString(tx, ty - lh * 2, f"Date: {d_part}")
    if t_part:
        can.drawString(tx, ty - lh * 3, t_part)

    can.save()
    packet.seek(0)
    return packet.getvalue()

with open("vivan_birth_certificate_original_signed.pdf", "rb") as f:
    pdf_bytes = f.read()

reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
writer = pypdf.PdfWriter()

p0 = reader.pages[0]
pw = float(p0.mediabox.width)
ph = float(p0.mediabox.height)

overlay = create_exact_adobe_stamp_overlay(pw, ph, [450, 158, 500, 208], "AMIT GARG", "2026.01.03 16:05:08 +05:30")
overlay_reader = pypdf.PdfReader(io.BytesIO(overlay))

if '/Annots' in p0:
    p0[pypdf.generic.NameObject('/Annots')] = pypdf.generic.ArrayObject([
        a for a in p0['/Annots']
        if not (a.get_object().get('/FT') == '/Sig' or a.get_object().get('/Type') == '/Sig')
    ])

p0.merge_page(overlay_reader.pages[0])
writer.add_page(p0)

out = io.BytesIO()
writer.write(out)

with open("final_vivan_stamped.pdf", "wb") as f:
    f.write(out.getvalue())

doc = pymupdf.open("final_vivan_stamped.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=200)
pix.save("final_full_page.png")

im = Image.open("final_full_page.png")
w, h = im.size
crop_box = (int(w * 0.65), int(h * 0.68), int(w * 0.95), int(h * 0.85))
cropped = im.crop(crop_box)
cropped.save("final_vivan_crop.png")
print("Saved final_vivan_crop.png successfully")
