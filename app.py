import streamlit as st
import random
from datetime import datetime

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
    """
    Generate random items such that total ~ target_total (±5%)
    """
    items_list = list(ITEMS.items())
    invoice = []
    total = 0
    tries = 0

    while abs(total - target_total) > target_total * 0.05 and tries < 300:
        invoice.clear()
        total = 0
        tries += 1

        # Random number of items per invoice (5 to 10)
        num_items = random.randint(5, 10)
        selected_items = random.sample(items_list, num_items)

        for name, price in selected_items:
            # Base quantity logic scaled by total
            # e.g. for 1 lakh invoice, quantities will be larger than small invoices
            max_qty = max(1, int(target_total / (price * num_items * random.uniform(1.5, 3.5))))
            qty = random.randint(1, max_qty)
            item_total = qty * price

            invoice.append((name, qty, price, item_total))
            total += item_total

        # Fine-tuning adjustment
        if total < target_total * 0.9:
            scale_factor = target_total / max(total, 1)
            invoice = [(n, int(q * scale_factor * 0.9), p, int(q * scale_factor * 0.9) * p) for n, q, p, _ in invoice]
            total = sum(i[3] for i in invoice)

    return invoice, int(total)


# ---------------------------
# 3️⃣ Streamlit UI
# ---------------------------
st.set_page_config(page_title="Smart Invoice Generator", page_icon="🧾", layout="centered")
st.title("🧾 Smart Invoice Generator (No PDF)")
st.write("Automatically generate random invoices that total your daily sales!")

total_sales = st.number_input("Enter Total Sales (₹):", min_value=1000, step=1000, value=150000)
min_invoices = st.number_input("Minimum number of invoices:", 5, 50, 10)
max_invoices = st.number_input("Maximum number of invoices:", 5, 50, 15)

if st.button("Generate Invoices"):
    num_invoices = random.randint(min_invoices, max_invoices)
    st.info(f"Generating {num_invoices} invoices for ₹{total_sales:,} total sales...")
    invoice_totals = split_total(total_sales, num_invoices)

    total_sum = 0
    for i, t in enumerate(invoice_totals, start=1):
        items, real_total = generate_invoice_items(t)
        total_sum += real_total

        with st.expander(f"📄 Invoice #{i}  —  Total ₹{real_total:,}"):
            st.write(f"**Date:** {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            st.table(
                {
                    "Item": [x[0] for x in items],
                    "Qty": [x[1] for x in items],
                    "Price (₹)": [x[2] for x in items],
                    "Total (₹)": [x[3] for x in items],
                }
            )

    st.success(f"✅ Generated {num_invoices} invoices successfully!")
    st.info(f"💰 Total of all invoices: ₹{total_sum:,}")
