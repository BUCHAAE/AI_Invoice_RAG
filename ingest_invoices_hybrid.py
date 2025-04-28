import os
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
persist_directory = "chroma_db"
csv_path = "invoice_summary.csv"
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"

# --- Step 1: Read CSV ---
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"\u274c Couldn't find {csv_path}. Please run invoice creation first!")

print(f"\ud83d\udd0d Reading CSV from {csv_path}...")

df = pd.read_csv(csv_path)

# --- Step 2: Create text chunks ---
print("\ud83d\udcc3 Creating text chunks for vectorstore...")

documents = []

for _, row in df.iterrows():
    # Construct meaningful text from structured fields
    full_text = (
        f"Invoice {row['InvoiceNumber']} for {row['DogName']} in {row['Month']} {row['Year']}. "
        f"Days attended: {row['DaysAttended']}. "
        f"Original cost per day: ${row['OriginalCostPerDay']}. "
        f"Discount applied: {row['DiscountApplied']}%. "
        f"Discounted cost per day: ${row['DiscountedCostPerDay']}. "
        f"Total cost: ${row['TotalCost']}."
    )
    documents.append(full_text)

if not documents:
    print("⚠️ No text documents created. Exiting...")
    exit(1)

# --- Step 3: Split into smaller chunks if needed (not really needed here, but structured) ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
all_texts = text_splitter.split_text("\n".join(documents))

print(f"\ud83d\udd39 Created {len(all_texts)} text chunks.")

# --- Step 4: Create embeddings ---
print("\ud83d\udd22 Building embeddings...")

embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

# --- Step 5: Create and persist Chroma vectorstore ---
print("\ud83d\udcca Saving to Chroma database...")

if os.path.exists(persist_directory):
    import shutil
    shutil.rmtree(persist_directory)

vectorstore = Chroma.from_texts(all_texts, embedding=embeddings, persist_directory=persist_directory)
vectorstore.persist()

print("✅ Vectorstore created successfully and saved to 'chroma_db'.")

