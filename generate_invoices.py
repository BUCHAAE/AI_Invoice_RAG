from fpdf import FPDF
import calendar
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# === Paths ===
output_folder = "invoices"
os.makedirs(output_folder, exist_ok=True)

# === Constants ===
provider_name = "Pawprints and Playcare LLC"
provider_address = "7427 Willow Creek Drive\nSuite 210\nBloomington, MN 55439\nUSA"
customer_name = "Charlie Brown"
customer_address = "32 Willow Crescent\nBloomington, MN 55439\nUSA"
dog_name = "Snoopy"
cost_per_day = 22.50
discount_percentage = 50  # 50% discount
discounted_cost_per_day = cost_per_day * (1 - discount_percentage / 100)

# === Invoice date range ===
start_date = datetime(2022, 1, 1)
end_date = datetime(2025, 5, 31)

current_date = start_date
invoice_counter = 1

while current_date <= end_date:
    year = current_date.year
    month = current_date.month
    month_name = current_date.strftime("%B")

    # Find all Mondays
    mondays = []
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        if week[calendar.MONDAY] != 0:
            mondays.append(week[calendar.MONDAY])

    num_days = len(mondays)
    total_cost = num_days * discounted_cost_per_day

    # === Create PDF ===
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False, margin=10)
    pdf.add_page()

    # Draw black border
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)

    # Add logo
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=15, y=12, w=40)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Invoice: INV-{year}-{month:02d}", ln=True, align="R")

    pdf.ln(20)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"{provider_name}\n{provider_address}", align="L")
    pdf.ln(5)
    pdf.multi_cell(0, 8, f"Billed To:\n{customer_name}\n{customer_address}", align="L")

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Invoice for {month_name} {year}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Dog: {dog_name}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Dates Attended:", ln=True)
    for day in mondays:
        date_str = f"{day:02d}/{month:02d}/{year}"
        pdf.cell(0, 8, f"- {date_str}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"Original Cost per Day: ${cost_per_day:.2f}", ln=True)
    pdf.cell(0, 10, f"Discount Applied: {discount_percentage}%", ln=True)
    pdf.cell(0, 10, f"Discounted Cost per Day: ${discounted_cost_per_day:.2f}", ln=True)
    pdf.cell(0, 10, f"Total Days: {num_days}", ln=True)
    pdf.cell(0, 10, f"Total Amount Due: ${total_cost:.2f}", ln=True)

    # Save PDF
    filename = f"invoice_INV-{year}-{month:02d}.pdf"
    filepath = os.path.join(output_folder, filename)
    pdf.output(filepath)

    print(f"✅ Created {filename}")

    # Move to next month
    if month == 12:
        current_date = datetime(year + 1, 1, 1)
    else:
        current_date = datetime(year, month + 1, 1)

print("\n✅✅ All invoices created successfully!")
