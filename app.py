import streamlit as st
import random
from datetime import datetime
from io import BytesIO
import base64

# ---------------------------
# Store Config (edit freely)
# ---------------------------
SHOP = {
    "title_gu": "મારુતિ એજન્સી",
    "address_line": "શુભમ કોમ્પલેક્ષ, નેત્રંગ રોડ, રાજપારડી, જી. ભરૂચ.",
    "mobile": "94291 26777",
    "gst": "24AGVPM7286K1ZH"
}

ITEMS = {
    "Rice": 80, "Sugar": 45, "Oil": 150, "Flour": 55, "Tea": 180,
    "Coffee": 250, "Dal": 120, "Salt": 25, "Biscuits": 60, "Ghee": 550,
    "Spices": 200, "Nuts": 800, "Atta": 52, "Poha": 70, "Rusk": 48
}

# ---------------------------
# Helpers
# ---------------------------
def split_total(total, n):
    parts = [random.random() for _ in range(n)]
    factor = total / max(sum(parts), 1)
    return [max(1, round(p * factor)) for p in parts]

def generate_invoice_items(target_total):
    """
    Fills invoice close to target_total (±5%) with scaled quantities.
    """
    items_list = list(ITEMS.items())
    tries = 0
    while tries < 300:
        tries += 1
        selected = random.sample(items_list, k=random.randint(5, 10))
        rows = []
        subtotal = 0
        # rough distribution of target across items
        per_item_target = target_total / max(len(selected), 1)
        for name, price in selected:
            # scale qty to reach per-item target
            base_qty = max(1, int(per_item_target / price * random.uniform(0.7, 1.3)))
            qty = max(1, base_qty)
            amount = qty * price
            rows.append((name, price, qty, "0%", amount))
            subtotal += amount

        # fine tune
        if subtotal < target_total * 0.9:
            scale = target_total / max(subtotal, 1)
            new_rows = []
            subtotal = 0
            for (n, p, q, gst, amt) in rows:
                q2 = max(1, int(q * scale * 0.95))
                amt2 = q2 * p
                new_rows.append((n, p, q2, gst, amt2))
                subtotal += amt2
            rows = new_rows

        if abs(subtotal - target_total) <= target_total * 0.05:
            return rows, int(subtotal)

    # fallback
    return rows, int(subtotal)

def build_print_html(invoices, total_sum):
    """
    Returns a complete HTML string with A4 print CSS.
    Each invoice rendered on its own page.
    """
    css = """
    <style>
      @page { size: A4; margin: 10mm; }
      body { font-family: Arial, Helvetica, sans-serif; color: #000; }
      .sheet { width: 190mm; min-height: 277mm; margin: 0 auto 10mm auto; }
      .page-break { page-break-after: always; }
      .hdr-red { background: #c00000; color: #fff; padding: 8px 0; text-align: center; font-weight: 700; font-size: 20px; }
      .subline { text-align:center; font-size: 11px; margin-top: 2px; }
      .gstline { text-align:center; font-weight: bold; font-size: 11px; margin-top: 1px; }
      .row { display:flex; justify-content: space-between; font-size: 12px; margin: 10px 0 6px 0; }
      .label { font-weight: 600; }
      table { width: 100%; border-collapse: collapse; }
      th, td { border: 1px solid #c00; padding: 6px; font-size: 12px; }
      th { background: #f3f3f3; }
      .total-row th, .total-row td { font-weight: 700; }
      .footer { margin-top: 12px; font-size: 11px; display:flex; justify-content: space-between; }
      .jur { font-size: 10px; }
      .sign { font-weight: 700; }
      .totals { text-align: right; font-weight: 700; }
      .t-right { text-align: right; }
      .t-center { text-align: center; }
    </style>
    """
    pages = []
    for inv in invoices:
        bill_no = inv["bill_no"]
        customer = inv["customer"]
        items = inv["items"]
        inv_total = sum(r[-1] for r in items)
        rows_html = ""
        for (name, rate, qty, gst, amt) in items:
            rows_html += f"""
            <tr>
              <td>{name}</td>
              <td class="t-center">{rate}</td>
              <td class="t-center">{qty}</td>
              <td class="t-center">{gst}</td>
              <td class="t-right">₹ {amt:,}</td>
            </tr>
            """
        page = f"""
        <section class="sheet page-break">
          <div class="hdr-red">{SHOP['title_gu']}</div>
          <div class="subline">{SHOP['address_line']} &nbsp;&nbsp; M: {SHOP['mobile']}</div>
          <div class="gstline">GST : {SHOP['gst']}</div>

          <div class="row">
            <div><span class="label">નામ :</span> {customer}</div>
            <div><span class="label">બીલ નંબર :</span> {bill_no}</div>
            <div><span class="label">તારીખ :</span> {datetime.now().strftime('%d-%m-%Y')}</div>
          </div>

          <table>
            <thead>
              <tr>
                <th>ITEM</th>
                <th>RATE</th>
                <th>WEIGHT NOS</th>
                <th>GST</th>
                <th>AMOUNT</th>
              </tr>
            </thead>
            <tbody>
              {rows_html}
              <tr class="total-row">
                <td colspan="4" class="t-right">TOTAL</td>
                <td class="t-right">₹ {inv_total:,}</td>
              </tr>
            </tbody>
          </table>

          <div class="footer">
            <div class="jur">Subject to Jhagadia Jurisdiction</div>
            <div class="sign">વતી, મારુતિ એજન્સી</div>
          </div>
        </section>
        """
        pages.append(page)

    html = f"""<!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">{css}</head>
    <body>
      {''.join(pages)}
    </body>
    </html>"""
    return html

def html_download_button(html_str, filename, label):
    b = html_str.encode("utf-8")
    st.download_button(
        label=label,
        data=b,
        file_name=filename,
        mime="text/html"
    )

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Maruti Agency - Print Bills (HTML)", page_icon="🧾", layout="centered")
st.title("🧾 Maruti Agency — Print-Ready Bills (HTML)")

total_sales = st.number_input("Enter Total Sales (₹):", min_value=1000, step=1000, value=150000)
min_invoices = st.number_input("Minimum invoices:", 5, 100, 10)
max_invoices = st.number_input("Maximum invoices:", 5, 100, 15)
customer_base = st.text_input("Customer name prefix (for demo)", value="Customer")

if st.button("Generate Bills"):
    n = random.randint(min_invoices, max_invoices)
    st.info(f"Generating {n} invoices for ₹{total_sales:,} total sales...")

    targets = split_total(total_sales, n)
    invoices = []
    total_sum = 0

    for i, t in enumerate(targets, start=1):
        items, real_total = generate_invoice_items(t)
        total_sum += real_total
        invoices.append({
            "bill_no": f"{datetime.now():%y%m%d}-{i:03d}",
            "customer": f"{customer_base} {i}",
            "items": items
        })

    st.success(f"✅ Generated {n} invoices. Total of all invoices: ₹{total_sum:,}")

    # Build HTML
    html = build_print_html(invoices, total_sum)

    # Preview inside Streamlit
    st.subheader("Preview")
    # Use components to render HTML preview
    st.components.v1.html(html, height=900, scrolling=True)

    # Download as HTML
    html_download_button(html, f"Maruti_Invoices_{datetime.now():%Y%m%d_%H%M}.html",
                         "📥 Download Print-Ready HTML")

    st.caption("Tip: Open the downloaded HTML in your browser and press Ctrl/Cmd + P → Print to A4 (100%)")