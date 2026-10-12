import io
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def test_adobe_stamp(scale=32.0):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(200, 200))
    
    cx, cy = 100, 90
    cw = scale
    ch = scale * (133.0 / 132.0)
    
    # Checkmark position
    ck_x = cx - cw * 0.10
    ck_y = cy - ch * 0.50

    # 1. "Signature valid" in Times-Roman
    can.setFont("Times-Roman", 12.0)
    can.setFillColor(colors.HexColor("#000000"))
    # Centered above the entire signature composition
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

    # Green Checkmark
    can.setFillColor(colors.HexColor("#00962E"))
    p_gr = can.beginPath()
    p_gr.moveTo(*to_c(*pts[0]))
    for pt in pts[1:]:
        p_gr.lineTo(*to_c(*pt))
    p_gr.close()
    can.drawPath(p_gr, fill=1, stroke=0)

    # 3. Overlaid Signer Text
    # Overlaid text starts ~18pt to the left of the checkmark
    tx = ck_x - 18.0
    ty = ck_y + ch * 0.52
    lh = 8.8

    can.setFont("Helvetica", 7.6)
    can.setFillColor(colors.HexColor("#000000"))
    can.drawString(tx, ty, "Digitally signed by")
    can.drawString(tx, ty - lh, "AMIT GARG")
    can.drawString(tx, ty - lh * 2, "Date: 2026.01.03")
    can.drawString(tx, ty - lh * 3, "16:05:08 +05:30")

    can.save()
    packet.seek(0)
    
    with open("adobe_test_stamp.pdf", "wb") as f:
        f.write(packet.getvalue())

    # Render image
    doc = pymupdf.open("adobe_test_stamp.pdf")
    page = doc[0]
    pix = page.get_pixmap(dpi=200)
    pix.save("adobe_test_stamp.png")
    print("Rendered adobe_test_stamp.png successfully")

test_adobe_stamp()
