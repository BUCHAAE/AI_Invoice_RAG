#!/bin/bash
# Author: Andrew Buchanan
# Date: 26/04/2025
#
# Purpose:
# This shell script launches the Python menu interface 
# ('menu.py') to allow the user to interactively choose actions 
# such as cleaning the environment, creating invoices, or launching the system.


echo "🧹 Cleaning old files..."

# Delete generated CSVs, invoice PDFs, and vector database
rm -f invoice_summary.csv
rm -f attendance_detail.csv
rm -f invoice_count.txt
rm -rf invoices
rm -rf chroma_db

echo "✅ Cleanup complete."
mkdir chroma_db

echo "⚡ Generating fresh invoices..."

# Step 1: Generate invoices
python3 generate_invoices.py

echo "📄 Invoices generated."

echo "⚡ Building invoice CSV summaries..."

# Step 2: Build CSVs
python3 csv_builder.py

echo "📑 CSVs created."

echo "⚡ Creating vector database from invoices..."

# Step 3: Build vectorstore
python3 ingest_invoices_hybrid.py

echo "📦 Vectorstore built."

echo "✅ Rebuild complete."

echo "🚀 Launching Snoopy Q&A UI..."

# Step 4: Launch UI
python3 demo_ui_hybrid.py
