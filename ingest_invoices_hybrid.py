"""
Author: Andrew Buchanan
Date: 26/04/2025

Purpose:
This script processes structured CSVs created from daycare invoices and attendance records.
It builds a semantic vectorstore using sentence-transformer embeddings for retrieval-augmented generation.
It also includes static facts such as the earliest attendance date to improve accuracy.
"""

import os
import pandas as pd
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
persist_directory = "chroma_db"
invoice_csv = "invoice_summary.csv"
attendance_csv = "attendance_detail.csv"
embedding_model_name = "BAAI/bge-small-en"

# --- Load CSVs ---
if not os.path.exists(invoice_csv) or not os.path.exists(attendance_csv):
    raise FileNotFoundError("❌ Required CSV files are missing. Please generate them first.")

print(f"📄 Reading {invoice_csv} and {attendance_csv}...")
invoice_df = pd.read_csv(invoice_csv)
attendance_df = pd.read_csv(attendance_csv)

invoice_df['TotalAmountDue'] = pd.to_numeric(invoice_df['TotalAmountDue'], errors='coerce').fillna(0)
attendance_df["ParsedDate"] = pd.to_datetime(attendance_df["Date"], format="%d/%m/%Y", errors="coerce")

documents = []

# --- Invoices as text chunks ---
for _, row in invoice_df.iterrows():
    invoice_text = (
        f"Invoice Number: {row['InvoiceNumber']}. "
        f"Month Billed: {row['MonthBilledFor']}. "
        f"Year: {row['Year']}. "
        f"Client: {row['ClientName']}, Address: {row['ClientAddress']}. "
        f"Service Provider: {row['ServiceProviderName']}, Address: {row['ServiceProviderAddress']}. "
        f"Dog Name: {row['DogName']}. "
        f"Cost Per Day: ${row['OriginalCostPerDay']}, Discount: {row['PercentageDiscount']}%. "
        f"Total Due: ${row['TotalAmountDue']}. "
        f"Days Attended: {row['DatesAttendedCount']}."
    )
    documents.append(invoice_text)

# --- Attendance as text chunks, with year explicitly included ---
attendance_years = set()
for _, row in attendance_df.iterrows():
    try:
        date_obj = datetime.strptime(row['Date'], "%d/%m/%Y")
        attendance_years.add(date_obj.year)
        documents.append(
            f"{row['DogName']} attended on {row['Date']} ({row['Day']}) in {date_obj.year} under invoice {row['InvoiceNumber']}."
        )
    except:
        documents.append(
            f"{row['DogName']} attended on {row['Date']} ({row['Day']}) under invoice {row['InvoiceNumber']}."
        )

# --- Static facts ---
first_attendance = attendance_df["ParsedDate"].min()
if pd.notnull(first_attendance):
    documents.append(f"Snoopy first attended daycare on {first_attendance.strftime('%d/%m/%Y')}.")

# Invoice summary
documents.append(f"There are {len(invoice_df)} invoices in total.")
documents.append(f"The total cost for all invoices is ${invoice_df['TotalAmountDue'].sum():.2f}.")

# Attendance year summary
sorted_years = sorted(attendance_years)
if sorted_years:
    documents.append("Snoopy attended doggy daycare in the following years: " + ", ".join(str(y) for y in sorted_years))

# --- Chunking ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_text("\n".join(documents))

if os.path.exists(persist_directory):
    import shutil
    shutil.rmtree(persist_directory)

embedding = HuggingFaceEmbeddings(model_name=embedding_model_name)
vectorstore = Chroma.from_texts(chunks, embedding=embedding, persist_directory=persist_directory)

print("✅ Vectorstore created successfully.")
