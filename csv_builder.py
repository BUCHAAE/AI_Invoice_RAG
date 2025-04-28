import os
import pandas as pd
import pdfplumber

# Define input/output paths
invoices_dir = "invoices"
invoice_summary_csv = "invoice_summary.csv"
attendance_detail_csv = "attendance_detail.csv"

# Initialise data lists
invoice_data = []
attendance_data = []

# Process each PDF invoice
for filename in sorted(os.listdir(invoices_dir)):
    if filename.endswith(".pdf"):
        filepath = os.path.join(invoices_dir, filename)
        print(f"Processing {filename}...")

        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

            lines = text.splitlines()
            invoice_number = None
            month_year = None
            dog_name = None
            dates_attended = []
            original_cost_per_day = None
            discount_applied = None
            discounted_cost_per_day = None
            total_amount_due = None

            for line in lines:
                line = line.strip()
                if line.startswith("Invoice:"):
                    invoice_number = line.split("Invoice:")[1].strip()
                if "Invoice for" in line:
                    month_year = line.split("Invoice for")[1].strip()
                if line.startswith("Dog:"):
                    dog_name = line.split("Dog:")[1].strip()
                if line.startswith("- ") and "/" in line:
                    dates_attended.append(line[2:].strip())
                if line.startswith("Original Cost per Day:"):
                    original_cost_per_day = float(line.split("$")[1].strip())
                if line.startswith("Discount Applied:"):
                    discount_applied = int(line.split("%")[0].split()[-1].strip())
                if line.startswith("Discounted Cost per Day:"):
                    discounted_cost_per_day = float(line.split("$")[1].strip())
                if line.startswith("Total Amount Due:"):
                    total_amount_due = float(line.split("$")[1].strip())

            if invoice_number and month_year:
                try:
                    month_name, year = month_year.split()
                    year = int(year)
                except ValueError:
                    month_name = "Unknown"
                    year = 0

                invoice_data.append({
                    "InvoiceNumber": invoice_number,
                    "Year": year,
                    "Month": month_name,
                    "DogName": dog_name,
                    "DaysAttended": len(dates_attended),
                    "OriginalCostPerDay": original_cost_per_day,
                    "DiscountApplied": discount_applied,
                    "DiscountedCostPerDay": discounted_cost_per_day,
                    "TotalCost": total_amount_due,
                    "InvoiceText": text  # Full extracted text
                })

                for date in dates_attended:
                    attendance_data.append({
                        "InvoiceNumber": invoice_number,
                        "DogName": dog_name,
                        "DateAttended": date
                    })

# Create dataframes
invoice_df = pd.DataFrame(invoice_data)
attendance_df = pd.DataFrame(attendance_data)

# Sort invoice summary by Year and Month
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

invoice_df["MonthNumber"] = invoice_df["Month"].map(month_order)
invoice_df = invoice_df.sort_values(by=["Year", "MonthNumber"]).drop(columns=["MonthNumber"])

# Save to CSV
invoice_df.to_csv(invoice_summary_csv, index=False)
attendance_df.to_csv(attendance_detail_csv, index=False)

print(f"\u2705 Saved invoice summary to {invoice_summary_csv}")
print(f"\u2705 Saved attendance detail to {attendance_detail_csv}")
print("\u2705 Done.")
