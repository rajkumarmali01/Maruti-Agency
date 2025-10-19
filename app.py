from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import inflect

# -------------------------------------------------------
# 1️⃣ Number to Words Helper
# -------------------------------------------------------
def num2words(num):
    p = inflect.engine()
    return p.number_to_words(num, andword="").replace(",", "").title()

# -------------------------------------------------------
# 2️⃣ Maruti Agency Bill Class
# -------------------------------------------------------
class MarutiBill(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.set_margins(left=10, top=10, right=10)

    # ---------- Header ----------
    def header(self):
        self.set_draw_color(200, 0, 0)
        self.set_fill_color(200, 0, 0)
        self.rect(10, 10, 190, 15, 'F')

        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "મારુતિ એજન્સી", align="C", ln=1)

        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", size=9)
        self.set_xy(10, 26)
        self.cell(0, 5, "શુભમ કોમ્પલેક્ષ, નેત્રંગ રોડ, રાજપારડી, જી. ભરૂચ.   M: 94291 26777", ln=1, align="C")
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 5, "GST : 24AGVPM7286K1ZH", ln=1, align="C")

    # ---------- Footer ----------
    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", size=9)
        self.cell(0, 5, "Subject to Jhagadia Jurisdiction", ln=1, align="L")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, "વતી, મારુતિ એજન્સી", ln=1, align="R")

    # ---------- Bill Drawing ----------
    def draw_bill(self, bill_no, customer_name, items):
        self.add_page()
        self.set_font("Helvetica", size=11)

        # Customer / Bill / Date Line
        self.set_xy(15, 42)
        self.cell(90, 8, f"નામ : {customer_name}")
        self.cell(50, 8, f"બીલ નંબર : {bill_no}")
        self.cell(40, 8, f"તારીખ : {datetime.now().strftime('%d-%m-%Y')}", ln=1)

        # Table Header
        headers = ["ITEM", "RATE", "WEIGHT NOS", "GST", "AMOUNT"]
        col_widths = [70, 30, 30, 25, 35]
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(240, 240, 240)
        y_start = 55
        x = 15
        for i, head in enumerate(headers):
            self.rect(x, y_start, col_widths[i], 10)
            self.cell(col_widths[i], 10, head, align="C", fill=True)
            x += col_widths[i]
        self.ln()

        # Table Rows
        self.set_font("Helvetica", size=10)
        y = y_start + 10
        total = 0
        for (item, rate, qty, gst, amt) in items:
            x = 15
            for val, w in zip([item, rate, qty, gst, amt], col_widths):
                self.rect(x, y, w, 8)
                self.cell(w, 8, str(val), align="C")
                x += w
            total += amt
            y += 8

        # Total Row
        self.set_font("Helvetica", "B", 11)
        self.rect(15, y, sum(col_widths[:-1]), 10)
        self.cell(sum(col_widths[:-1]), 10, "TOTAL", align="R")
        self.rect(15 + sum(col_widths[:-1]), y, col_widths[-1], 10)
        self.cell(col_widths[-1], 10, f"₹ {total}", align="C", ln=1)

        # Amount in Words
        self.set_y(y + 15)
        self.set_font("Helvetica", size=10)
        self.cell(0, 6, f"Rs. in Words : {num2words(total)} Only", ln=1)

        # Printed Timestamp
        self.ln(4)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 6, f"Printed on : {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=1, align="R")

# -------------------------------------------------------
# 3️⃣ Example – Generate One Print-Ready Bill
# -------------------------------------------------------
if __name__ == "__main__":
    items = [
        ("Rice", 80, 10, "5%", 800),
        ("Sugar", 45, 5, "5%", 225),
        ("Oil", 150, 2, "5%", 300),
        ("Tea", 180, 1, "5%", 180),
        ("Salt", 25, 4, "0%", 100)
    ]

    pdf = MarutiBill()
    pdf.draw_bill("001", "Rajesh Patel", items)

    pdf.output("Maruti_Bill_Print.pdf")
    print("✅ Print-ready Maruti Agency bill generated: Maruti_Bill_Print.pdf")