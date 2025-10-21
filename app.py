import streamlit as st
import pandas as pd
import random
from datetime import datetime
import base64

# -------------------------------------------------------
# 1️⃣  Shop details (edit freely)
# -------------------------------------------------------
SHOP = {
    "name": "Maruti Agency",
    "address": "Shubham Complex, Netrang Road, Rajpardi, Dist. Bharuch",
    "mobile": "94291 26777",
    "gst": "24AGVPM7286K1ZH"
}

# -------------------------------------------------------
# 2️⃣  Load default CSVs (auto from repo)
# -------------------------------------------------------
@st.cache_data
def load_default_data():
    items_df = pd.read_csv("items_db.csv")
    customers_df = pd.read_csv("customers_db.csv")
    return items_df, customers_df

items_df, customers_df = load_default_data()

# Optional upload overrides
st.sidebar.header("🔄 Optional Uploads")
items_file = st.sidebar.file_uploader("Upload new Items CSV", type=["csv"])
if items_file:
    items_df = pd.read_csv(items_file)
    st.sidebar.success("Using uploaded item list.")

customers_file = st.sidebar.file_uploader("Upload new Customers CSV", type=["csv"])
if customers_file:
    customers_df = pd.read_csv(customers_file)
    st.sidebar.success("Using uploaded customers list.")

# -------------------------------------------------------
# 3️⃣  Streamlit inputs
# -------------------------------------------------------
st.title("🧾 Maruti Agency – English Billing System")

total_sales = st.number_input("Total Sales (₹)", min_value=1000, step=1000, value=150000)
min_invoices = st.number_input("Minimum Invoices", 1, 100, 5)
max_invoices = st.number_input("Maximum Invoices", 1, 100, 10)
bill_date = st.date_input("Select Bill Date", datetime.today())

# -------------------------------------------------------
# 4️⃣  Helper functions
# -------------------------------------------------------
def split_total(total, n):
    parts = [random.random() for _ in range(n)]
    factor = total / sum(parts)
    return [round(p * factor) for p in parts]

def generate_invoice_items(target_total, items_df):
    items_list = items_df.to_dict("records")
    tries = 0
    while tries < 300:
        tries += 1
        selected = random.sample(items_list, k=random.randint(5, 10))
        rows, subtotal = [], 0
        per_item_target = target_total / len(selected)
        for it in selected:
            price, gst = it["price"], it["gst"]
            qty = max(1, int(per_item_target / price * random.uniform(0.8, 1.2)))
            amount = qty * price
            gst_amount = round(amount * gst / 100, 2)
            rows.append((it["item_name"], price, qty, gst, gst_amount, amount))
            subtotal += amount + gst_amount
        if abs(subtotal - target_total) <= target_total * 0.05:
            return rows, round(subtotal, 2)
    return rows, round(subtotal, 2)

def build_html(invoices):
    css = """
    <style>
      @page { size: A4; margin: 10mm; }
      body { font-family: Arial, Helvetica, sans-serif; color: #000; }
      .sheet { width:190mm; min-height:277mm; margin:auto; }
      .page-break { page-break-after: always; }
      .hdr { text-align:center; border-bottom:2px solid #c00; padding-bottom:4px; margin-bottom:8px; }
      .hdr h1 { margin:0; color:#c00; }
      .hdr p { margin:2px 0; font-size:11px; }
      table { width:100%; border-collapse:collapse; font-size:12px; }
      th, td { border:1px solid #999; padding:6px; }
      th { background:#f3f3f3; }
      .right { text-align:right; }
      .bold { font-weight:700; }
      .footer { margin-top:10px; display:flex; justify-content:space-between; font-size:11px; }
      .jur { font-style:italic; }
    </style>
    """
    pages = []
    for inv in invoices:
        customer = inv["customer"]
        bill_no = inv["bill_no"]
        date = inv["date"]
        items = inv["items"]

        subtotal = sum(i[5] for i in items)
        total_gst = sum(i[4] for i in items)
        grand_total = round(subtotal + total_gst, 2)

        rows = ""
        for (name, rate, qty, gst, gst_amt, amt) in items:
            rows += f"""
            <tr>
              <td>{name}</td>
              <td class='right'>{rate}</td>
              <td class='right'>{qty}</td>
              <td class='right'>{gst}%</td>
              <td class='right'>₹{gst_amt}</td>
              <td class='right'>₹{amt}</td>
            </tr>
            """

        page = f"""
        <section class='sheet page-break'>
          <div class='hdr'>
            <h1>{SHOP['name']}</h1>
            <p>{SHOP['address']} &nbsp; | &nbsp; M: {SHOP['mobile']}</p>
            <p>GSTIN: {SHOP['gst']}</p>
          </div>

          <table>
            <tr>
              <td><b>Customer:</b> {customer}</td>
              <td><b>Bill No:</b> {bill_no}</td>
              <td><b>Date:</b> {date}</td>
            </tr>
          </table><br>

          <table>
            <thead>
              <tr>
                <th>Item</th><th>Rate</th><th>Qty</th>
                <th>GST %</th><th>GST Amt</th><th>Total</th>
              </tr>
            </thead>
            <tbody>
              {rows}
              <tr class='bold'>
                <td colspan='5' class='right'>Subtotal</td>
                <td class='right'>₹{subtotal:.2f}</td>
              </tr>
              <tr class='bold'>
                <td colspan='5' class='right'>Total GST</td>
                <td class='right'>₹{total_gst:.2f}</td>
              </tr>
              <tr class='bold'>
                <td colspan='5' class='right'>Grand Total</td>
                <td class='right'>₹{grand_total:.2f}</td>
              </tr>
            </tbody>
          </table>

          <div class='footer'>
            <div class='jur'>Subject to Jhagadia Jurisdiction</div>
            <div class='sign'>For {SHOP['name']}</div>
          </div>
        </section>
        """
        pages.append(page)
    return f"<!DOCTYPE html><html><head>{css}</head><body>{''.join(pages)}</body></html>"

def html_download_button(html, filename, label):
    st.download_button(label, html.encode("utf-8"), file_name=filename, mime="text/html")

# -------------------------------------------------------
# 5️⃣  Generate invoices
# -------------------------------------------------------
if st.button("Generate Bills"):
    num_invoices = random.randint(min_invoices, max_invoices)
    st.info(f"Generating {num_invoices} invoices for ₹{total_sales:,} total sales...")

    targets = split_total(total_sales, num_invoices)
    invoices, total_sum = [], 0

    for i, t in enumerate(targets, start=1):
        items, bill_total = generate_invoice_items(t, items_df)
        customer = random.choice(customers_df["customer_name"].tolist())
        invoices.append({
            "bill_no": f"{datetime.now():%y%m%d}-{i:03d}",
            "customer": customer,
            "date": bill_date.strftime("%d-%m-%Y"),
            "items": items
        })
        total_sum += bill_total

    st.success(f"✅ Generated {num_invoices} invoices totalling ₹{total_sum:,.2f}")

    html = build_html(invoices)
    st.components.v1.html(html, height=900, scrolling=True)
    html_download_button(html, f"Invoices_{datetime.now():%Y%m%d_%H%M}.html", "📥 Download Print-Ready HTML")
    st.caption("Tip: Open downloaded HTML in browser → Print → Save as PDF (A4, 100%)")