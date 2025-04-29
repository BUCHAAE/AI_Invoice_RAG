"""
Author: Andrew Buchanan
Date: 26/04/2025

Purpose:
This script processes the CSV files created from the invoices, 
creates a text-based vectorstore using a HuggingFace embedding model, 
and saves the resulting database using Chroma for fast retrieval.
It prepares the data for later Q&A interaction with the LLM.
"""

import os
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
persist_directory = "chroma_db"
csv_path = "invoice_summary.csv"
embedding_model_name = "BAAI/bge-small-en"

# --- Step 1: Read CSV ---
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"❌ Couldn't find {csv_path}. Please run invoice creation first!")

print(f"🔍 Reading CSV from {csv_path}...")

df = pd.read_csv(csv_path)

# --- Step 2: Create text chunks ---
print("📃 Creating text chunks for vectorstore...")

documents = []

for _, row in df.iterrows():
    full_text = (
        f"Invoice Number: {row['InvoiceNumber']}. "
        f"Service Provider: {row['ServiceProviderName']} at {row['ServiceProviderAddress']}. "
        f"Client: {row['ClientName']} living at {row['ClientAddress']}. "
        f"Dog Name: {row['DogName']}. "
        f"Month Billed For: {row['MonthBilledFor']}. "
        f"Original Cost Per Day: ${row['OriginalCostPerDay']}. "
        f"Percentage Discount: {row['PercentageDiscount']}%. "
        f"Total Amount Due: ${row['TotalAmountDue']}. "
        f"Number of Attendance Days: {row['DatesAttendedCount']}."
    )
    documents.append(full_text)

if not documents:
    print("⚠️ No text documents created. Exiting...")
    exit(1)

# --- Step 3: Split into smaller chunks ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
all_texts = text_splitter.split_text("\n".join(documents))

print(f"🔹 Created {len(all_texts)} text chunks.")

# --- Step 4: Create embeddings ---
print("🔢 Building embeddings...")

embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

# --- Step 5: Create and persist Chroma vectorstore ---
print("📦 Saving to Chroma database...")

if os.path.exists(persist_directory):
    import shutil
    shutil.rmtree(persist_directory)

vectorstore = Chroma.from_texts(all_texts, embedding=embeddings, persist_directory=persist_directory)

# --- not required now
#vectorstore.persist()

print("✅ Vectorstore created successfully and saved to 'chroma_db'.")
