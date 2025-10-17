import streamlit as st
import random, os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO

# ---------------------------
# 1️⃣ Store Items (Editable)
# ---------------------------
ITEMS = {
    "Milk": 50, "Bread": 30, "Butter": 120, "Cheese": 200, "Juice": 90,
    "Rice": 80, "Sugar": 45, "Oil": 150, "Biscuits": 60, "Salt": 25,
    "Pulses": 140, "Flour": 55, "Paneer": 220, "Tea": 180, "Coffee": 250,
    "Chips": 35
}

# ---------------------------
# 2️⃣ Helper Functions
# ---------------------------
def split_total(total, n):
    parts = [random.random() for _ in range(n)]
    factor = total / sum(parts)
    return [round(p * factor) for p in parts]

def generate_invoice_items(target_total):
    items_list = list(ITEMS.items())
    invoice = []
    total = 0
    tries = 0
    while abs(total - target_total) > target_total * 0.05 and tries < 1000:
        invoice.clear()
        total = 0
        for name, price in random.sample(items_list, random.randint(4, 8)):
            qty = random.randint(1, 6)
            item_total = qty * price
            if total + item_total > target_total * 1.1:
                continue
            invoice.append((name, qty, price, item_total))
            total += item_total
        tries += 1
    return invoice, total

def create_combined_pdf(invoices):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    for inv_no, (items, total) in enumerate(invoices, start=1):
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 30, f"STORE INVOICE #{inv_no}")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 60, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        c.line(50, height - 70, width - 50, height - 70)

        y = height - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Item")
        c.drawString(220, y, "Qty")
        c.drawString(280, y, "Price")
        c.drawString(360, y, "Total")
        y -= 20
        c.setFont("Helvetica", 11)

        for name, qty, price, item_total in items:
            c.drawString(50, y, name)
            c.drawString(220, y, str(qty))
            c.drawString(280, y, f"₹{price}")
            c.drawString(360, y, f"₹{item_total}")
            y -= 18
            if y < 100:
                c.showPage()
                y = height - 100

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.darkblue)
        c.drawRightString(width - 50, y - 20, f"TOTAL: ₹{total}")
        c.showPage()  # move to next page for next invoice

    c.save()
    buffer.seek(0)
    return buffer

# ---------------------------
# 3️⃣ Streamlit UI
# ---------------------------
st.set_page_config(page_title="Smart Invoice Generator", page_icon="🧾", layout="centered")
st.title("🧾 Smart Invoice Generator")
st.write("Automatically generate random invoices that total your daily sales!")

total_sales = st.number_input("Enter Total Sales (₹):", min_value=1000, step=1000, value=150000)
min_invoices = st.number_input("Minimum number of invoices:", 5, 50, 10)
max_invoices = st.number_input("Maximum number of invoices:", 5, 50, 15)

if st.button("Generate Invoices"):
    num_invoices = random.randint(min_invoices, max_invoices)
    st.info(f"Generating {num_invoices} invoices for ₹{total_sales:,} total sales...")
    invoice_totals = split_total(total_sales, num_invoices)

    invoices = []
    total_sum = 0
    for t in invoice_totals:
        items, real_total = generate_invoice_items(t)
        total_sum += real_total
        invoices.append((items, real_total))

    pdf_buffer = create_combined_pdf(invoices)
    st.success(f"✅ Generated {num_invoices} invoices! Total: ₹{total_sum:,}")

    st.download_button(
        label="📥 Download All Invoices (PDF)",
        data=pdf_buffer,
        file_name=f"All_Invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

