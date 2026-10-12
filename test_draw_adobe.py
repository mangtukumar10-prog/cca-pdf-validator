import os
import io
import datetime
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import pypdf

def draw_adobe_green_tick(can, cx, cy, size=36, signer="AMIT GARG", date_str="2026.01.03 16:05:08 +05:30"):
    """Draws the exact Adobe Acrobat Green Checkmark signature stamp.
    cx, cy: center coordinates of the signature box in PDF points
    size: width/height of the checkmark in points (default ~36pt)
    """
    can.saveState()

    # 1. "Signature valid" text in Times-Roman (Serif) centered above checkmark
    can.setFont("Times-Roman", 12.5)
    can.setFillColor(colors.black)
    can.drawCentredString(cx + 6, cy + size * 0.62, "Signature valid")

    # Normalized checkmark polygon vertices (from bottom-left (0,0) to (1,1))
    # Order: Left tip -> Left top -> Valley -> Top right -> Far right -> Bottom vertex
    # Scaled and translated around (cx, cy)
    pts = [
        (0.000, 0.391),  # Left tip
        (0.075, 0.474),  # Left top
        (0.320, 0.140),  # Inner valley
        (0.865, 1.000),  # Top right tip
        (1.000, 0.902),  # Far right corner
        (0.355, 0.000),  # Bottom vertex
    ]

    # Target box for the checkmark
    # Position checkmark slightly shifted to the right so overlaid text aligns nicely
    bx = cx - size * 0.35
    by = cy - size * 0.50
    w = size
    h = size

    def to_pt(nx, ny, ox=0, oy=0):
        return (bx + nx * w + ox, by + ny * h + oy)

    # 2. Draw Black Drop Shadow Polygon (offset slightly down and right)
    shadow_ox = size * 0.045
    shadow_oy = -size * 0.045
    can.setFillColor(colors.HexColor("#000000"))
    p_shadow = can.beginPath()
    p_shadow.moveTo(*to_pt(*pts[0], shadow_ox, shadow_oy))
    for pt in pts[1:]:
        p_shadow.lineTo(*to_pt(*pt, shadow_ox, shadow_oy))
    p_shadow.close()
    can.drawPath(p_shadow, fill=1, stroke=0)

    # 3. Draw Green Checkmark Polygon
    # Exact Adobe Green: #00A651 or #00962E
    can.setFillColor(colors.HexColor("#00962E"))
    p_green = can.beginPath()
    p_green.moveTo(*to_pt(*pts[0]))
    for pt in pts[1:]:
        p_green.lineTo(*to_pt(*pt))
    p_green.close()
    can.drawPath(p_green, fill=1, stroke=0)

    # 4. Overlaid Signer Text (Helvetica Sans-serif, black, clean line spacing)
    # Positioned over the checkmark exactly like the screenshot
    text_x = cx - size * 0.42
    text_y = cy + size * 0.16
    line_h = 7.5

    can.setFont("Helvetica", 6.5)
    can.setFillColor(colors.black)
    can.drawString(text_x, text_y, "Digitally signed by")
    can.drawString(text_x, text_y - line_h, signer)
    can.drawString(text_x, text_y - line_h * 2, f"Date: {date_str.split()[0] if ' ' in date_str else date_str}")
    if ' ' in date_str:
        can.drawString(text_x, text_y - line_h * 3, date_str.split(' ', 1)[1])

    can.restoreState()

# Test drawing on a blank 200x200 canvas
packet = io.BytesIO()
c = canvas.Canvas(packet, pagesize=(200, 200))
draw_adobe_green_tick(c, 100, 100, size=38, signer="AMIT GARG", date_str="2026.01.03 16:05:08 +05:30")
c.save()

packet.seek(0)
# Save as test PDF
with open("test_adobe_tick.pdf", "wb") as f:
    f.write(packet.getvalue())

print("Generated test_adobe_tick.pdf")
