#!/bin/bash
# Author: Andrew Buchanan
# Date: 26/04/2025
#
# Purpose:
# This shell script launches the Python menu interface 
# ('menu.py') to allow the user to interactively choose actions 
# such as cleaning the environment, creating invoices, or launching the system.

# Ensure script runs from project root
cd "$(dirname "$0")" || exit 1

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
python3 src/generate_invoices.py

echo "📄 Invoices generated."

echo "⚡ Building invoice CSV summaries..."

# Step 2: Build CSVs
python3 src/csv_builder.py

echo "📑 CSVs created."

echo "⚡ Creating vector database from invoices..."

# Step 3: Build vectorstore
python3 src/ingest_invoices_hybrid.py

echo "📦 Vectorstore built."

echo "✅ Rebuild complete."

echo "🚀 Launching Snoopy Q&A UI..."

# Step 4: Launch UI
python3 src/demo_ui_hybrid.py