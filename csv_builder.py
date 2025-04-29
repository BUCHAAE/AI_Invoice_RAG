import os
import sys
import pdfplumber
import pandas as pd
import re
from datetime import datetime
import contextlib

@contextlib.contextmanager
def suppress_stderr_real():
    """Actually suppress underlying system stderr prints."""
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    stderr_fd = os.dup(2)
    os.dup2(devnull_fd, 2)
    try:
        yield
    finally:
        os.dup2(stderr_fd, 2)
        os.close(devnull_fd)
        os.close(stderr_fd)

# Directories
invoice_dir = "invoices"
summary_csv = "invoice_summary.csv"
attendance_csv = "attendance_detail.csv"

# Lists to collect data
summary_data = []
attendance_data = []

# Read invoices
for filename in sorted(os.listdir(invoice_dir)):
    if filename.endswith(".pdf"):
        invoice_path = os.path.join(invoice_dir, filename)
        with suppress_stderr_real():  # <-- TRUE suppression
            with pdfplumber.open(invoice_path) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

        # Extract fields
        def extract_field(pattern, text, default=""):
            match = re.search(pattern, text)
            return match.group(1).strip() if match else default

        invoice_number = extract_field(r"Invoice Number:\s*(.+)", text)
        service_provider_name = extract_field(r"Service Provider Name:\s*(.+)", text)
        service_provider_address = extract_field(r"Service Provider Address:\s*(.+?)Client Name:", text, default="").replace("\n", " ").strip()
        client_name = extract_field(r"Client Name:\s*(.+)", text)
        client_address = extract_field(r"Client Address:\s*(.+?)Month Billed For:", text, default="").replace("\n", " ").strip()
        month_billed_for = extract_field(r"Month Billed For:\s*(.+)", text)
        dog_name = extract_field(r"Dog Name:\s*(.+)", text)
        original_cost_per_day = extract_field(r"Original Cost Per Day:\s*\$(\d+\.\d{2})", text)
        percentage_discount = extract_field(r"Percentage Discount:\s*(\d+)%", text)
        total_amount_due = extract_field(r"Total Amount Due:\s*\$(\d+\.\d{2})", text)

        # Extract all dates attended
        dates_attended = re.findall(r"\b(\d{2}/\d{2}/\d{4})\b", text)

        # Parse month and year
        try:
            billing_month, billing_year = month_billed_for.split()
        except ValueError:
            billing_month, billing_year = ("", "")

        # Save invoice summary
        summary_data.append({
            "InvoiceNumber": invoice_number,
            "ServiceProviderName": service_provider_name,
            "ServiceProviderAddress": service_provider_address,
            "ClientName": client_name,
            "ClientAddress": client_address,
            "MonthBilledFor": billing_month,
            "Year": billing_year,
            "DogName": dog_name,
            "OriginalCostPerDay": original_cost_per_day,
            "PercentageDiscount": percentage_discount,
            "TotalAmountDue": total_amount_due,
            "DatesAttendedCount": len(dates_attended)
        })

        # Save attendance details
        for date_str in dates_attended:
            try:
                dt = datetime.strptime(date_str, "%d/%m/%Y")
                attendance_data.append({
                    "InvoiceNumber": invoice_number,
                    "Date": date_str,
                    "Day": dt.strftime("%A"),
                    "DogName": dog_name
                })
            except Exception as e:
                print(f"⚠️ Error parsing date {date_str}: {e}")

# Save CSV files
pd.DataFrame(summary_data).to_csv(summary_csv, index=False)
pd.DataFrame(attendance_data).to_csv(attendance_csv, index=False)

print("✅ Saved invoice summary to invoice_summary.csv")
print("✅ Saved attendance detail to attendance_detail.csv")
print("✅ Done.")
