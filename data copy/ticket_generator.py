import pandas as pd
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import Color
from PIL import Image
import os

# --- Load background size ---
bg_img = Image.open("ticket_bg.png")
width_px, height_px = bg_img.size
DPI = 96

PAGE_WIDTH = width_px * 72 / DPI
PAGE_HEIGHT = height_px * 72 / DPI

# --- Paths ---
os.makedirs("output", exist_ok=True)
os.makedirs("qr", exist_ok=True)

df = pd.read_csv("tickets.csv")

GOLD = Color(212/255, 175/255, 55/255)

for _, row in df.iterrows():
    email = row["email"]
    ticket = row["ticket_id"]
    name = row["name"]

    # --- QR ---
    qr_path = f"qr/{ticket}.png"
    qrcode.make(ticket).save(qr_path)

    # --- PDF ---
    c = canvas.Canvas(
        f"output/{ticket}.pdf",
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT)
    )

    # Background
    c.drawImage(
        "ticket_bg.png",
        0, 0,
        width=PAGE_WIDTH,
        height=PAGE_HEIGHT
    )

    # =========================
    # QR CODE (centered)
    # =========================
    qr_size = 630 - 287  # 343
    qr_x = (PAGE_WIDTH - qr_size) / 2
    qr_y = 187

    c.drawImage(
        qr_path,
        qr_x,
        qr_y,
        width=qr_size,
        height=qr_size
    )

    # =========================
    # TEXT (gold)
    # =========================
    c.setFillColor(GOLD)

    # Email
    c.setFont("Helvetica", 20)
    c.drawCentredString(
        PAGE_WIDTH / 2,
        140,
        email
    )

    # Ticket ID
    c.setFont("Courier-Bold", 24)
    c.drawCentredString(
        PAGE_WIDTH / 2,
        100,
        f"Ticket ID: {ticket}"
    )

    c.showPage()
    c.save()