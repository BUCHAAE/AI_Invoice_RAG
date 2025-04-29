from fpdf import FPDF
import os
import random
import calendar


# Directory to store generated invoices
invoice_dir = "invoices"
os.makedirs(invoice_dir, exist_ok=True)

# Static values
service_provider_name = "Pawprints and Playcare LLC"
service_provider_address = "7427 Willow Creek Drive, Suite 210, Bloomington, MN 55439, USA"
client_name = "Charlie Brown"
client_address = "32 Willow Crescent, Bloomington, MN 55439, USA"
dog_name = "Snoopy"

# Invoice settings
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
years = [2022, 2023, 2024, 2025]

original_cost_per_day = 22.50
percentage_discount = 50


def generate_invoice(invoice_number, year, month, attendance_dates):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Invoice Number: {invoice_number}", ln=True)
    pdf.cell(200, 10, txt=f"Service Provider Name: {service_provider_name}", ln=True)
    pdf.multi_cell(0, 10, txt=f"Service Provider Address: {service_provider_address}")

    pdf.cell(200, 10, txt=f"Client Name: {client_name}", ln=True)
    pdf.multi_cell(0, 10, txt=f"Client Address: {client_address}")

    pdf.cell(200, 10, txt=f"Month Billed For: {month} {year}", ln=True)
    pdf.cell(200, 10, txt=f"Dog Name: {dog_name}", ln=True)

    pdf.cell(200, 10, txt=f"Dates Attended:", ln=True)
    for date in attendance_dates:
        pdf.cell(200, 10, txt=f"{date}", ln=True)

    total_days = len(attendance_dates)
    discounted_cost_per_day = original_cost_per_day * (1 - percentage_discount / 100)
    total_amount_due = total_days * discounted_cost_per_day

    pdf.cell(200, 10, txt=f"Original Cost Per Day: ${original_cost_per_day:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Percentage Discount: {percentage_discount}%", ln=True)
    pdf.cell(200, 10, txt=f"Discounted Cost Per Day: ${discounted_cost_per_day:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Amount Due: ${total_amount_due:.2f}", ln=True)

    output_path = os.path.join(invoice_dir, f"invoice_{invoice_number}.pdf")
    pdf.output(output_path)
    print(f"✅ Created {output_path}")


# Generate invoices
invoice_counter = 1
for year in years:
    for i, month in enumerate(months, start=1):
        invoice_number = f"INV-{year}-{i:02d}"
        last_day = calendar.monthrange(year, i)[1]
        possible_days = [d for d in [3, 10, 17, 24, 28] if d <= last_day]
        # Ensure only valid days for the month
        attendance_dates = [f"{day:02d}/{i:02d}/{year}" for day in possible_days if day <= last_day]
        attendance_dates = random.sample(attendance_dates, k=min(4, len(attendance_dates)))
        attendance_dates.sort(key=lambda x: int(x.split('/')[0]))
        generate_invoice(invoice_number, year, month, attendance_dates)

print("\n✅✅ All invoices created successfully!")
