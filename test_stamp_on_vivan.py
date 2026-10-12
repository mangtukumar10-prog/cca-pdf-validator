import io
import pypdf
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_adobe_green_tick_overlay(pw, ph, sig_rect, signer="AMIT GARG", date_str="2026.01.03 16:05:08 +05:30"):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(pw, ph))

    # Signature box coordinates from PDF
    if sig_rect and len(sig_rect) == 4:
        x1, y1, x2, y2 = sig_rect
        bx = min(x1, x2)
        by = min(y1, y2)
        bw = abs(x2 - x1)
        bh = abs(y2 - y1)
    else:
        # Default bottom-right coordinates on standard 612x792 page
        bx = 450
        by = 158
        bw = 50
        bh = 50

    cx = bx + bw / 2.0
    cy = by + bh / 2.0

    can.saveState()

    # 1. "Signature valid" text in Times-Roman (Serif)
    can.setFont("Times-Roman", 11)
    can.setFillColor(colors.black)
    can.drawCentredString(cx + 4, by + bh + 4, "Signature valid")

    # 2. Vector polygon for the checkmark
    # Checkmark dimensions inside the box
    cw = bw * 0.76  # ~38pt
    ch = bh * 0.76  # ~38pt
    # Position checkmark
    ck_x = bx + bw * 0.18
    ck_y = by + bh * 0.08

    # Normalized polygon points:
    # Left tip -> Left top -> Valley -> Top right -> Far right -> Bottom vertex
    pts = [
        (0.000, 0.400),  # 1. Left tip
        (0.070, 0.490),  # 2. Left top
        (0.315, 0.150),  # 3. Inner valley
        (0.855, 1.000),  # 4. Top right tip
        (1.000, 0.895),  # 5. Far right corner
        (0.350, 0.000),  # 6. Bottom vertex
    ]

    def to_canvas(nx, ny, ox=0, oy=0):
        return (ck_x + nx * cw + ox, ck_y + ny * ch + oy)

    # 3D Black Drop Shadow
    so_x = cw * 0.05
    so_y = -ch * 0.05
    can.setFillColor(colors.black)
    p_shadow = can.beginPath()
    p_shadow.moveTo(*to_canvas(*pts[0], so_x, so_y))
    for pt in pts[1:]:
        p_shadow.lineTo(*to_canvas(*pt, so_x, so_y))
    p_shadow.close()
    can.drawPath(p_shadow, fill=1, stroke=0)

    # Vivid Adobe Green Checkmark
    can.setFillColor(colors.HexColor("#00A651"))
    p_green = can.beginPath()
    p_green.moveTo(*to_canvas(*pts[0]))
    for pt in pts[1:]:
        p_green.lineTo(*to_canvas(*pt))
    p_green.close()
    can.drawPath(p_green, fill=1, stroke=0)

    # 3. Overlaid Signer Text
    # Formatted exactly like Adobe Reader:
    # Digitally signed by
    # <Signer>
    # Date: <YYYY.MM.DD>
    # <HH:MM:SS +TZ>
    can.setFont("Helvetica", 6.2)
    can.setFillColor(colors.black)
    tx = bx - 2
    ty = by + bh * 0.52
    lh = 7.2

    parts = date_str.split(" ", 1) if " " in date_str else [date_str, ""]
    d_part = parts[0]
    t_part = parts[1] if len(parts) > 1 else ""

    can.drawString(tx, ty, "Digitally signed by")
    can.drawString(tx, ty - lh, signer)
    can.drawString(tx, ty - lh * 2, f"Date: {d_part}")
    if t_part:
        can.drawString(tx, ty - lh * 3, t_part)

    can.restoreState()
    can.save()
    packet.seek(0)
    return packet.getvalue()

# Test stamping onto vivan_birth_certificate_original_signed.pdf
with open("vivan_birth_certificate_original_signed.pdf", "rb") as f:
    pdf_bytes = f.read()

reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
writer = pypdf.PdfWriter()

p0 = reader.pages[0]
pw = float(p0.mediabox.width)
ph = float(p0.mediabox.height)
sig_rect = [450, 158, 500, 208]

overlay = create_adobe_green_tick_overlay(pw, ph, sig_rect, "AMIT GARG", "2026.01.03 16:05:08 +05:30")
overlay_reader = pypdf.PdfReader(io.BytesIO(overlay))

# Remove original /Sig widget annotation so no corrupted signature flag
if '/Annots' in p0:
    p0[pypdf.generic.NameObject('/Annots')] = pypdf.generic.ArrayObject([
        a for a in p0['/Annots']
        if not (a.get_object().get('/FT') == '/Sig' or a.get_object().get('/Type') == '/Sig')
    ])

p0.merge_page(overlay_reader.pages[0])
writer.add_page(p0)

out = io.BytesIO()
writer.write(out)
stamped_pdf_bytes = out.getvalue()

with open("test_vivan_stamped.pdf", "wb") as f:
    f.write(stamped_pdf_bytes)

# Render bottom right corner to test_stamped_crop.png
doc = pymupdf.open("test_vivan_stamped.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=200)
pix.save("test_full_page.png")

# Crop the bottom right signature region
from PIL import Image
im = Image.open("test_full_page.png")
w, h = im.size
crop_box = (int(w * 0.65), int(h * 0.68), int(w * 0.95), int(h * 0.85))
cropped = im.crop(crop_box)
cropped.save("test_stamped_crop.png")
print("Saved test_stamped_crop.png successfully!")
