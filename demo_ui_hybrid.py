import gradio as gr
import pandas as pd
import os
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma

# === Helper to safely parse floats ===
def safe_float(x):
    try:
        return float(str(x).replace('$', '').replace(',', '').strip())
    except Exception:
        return 0.0

# === Load invoice summary CSV ===
csv_path = "invoice_summary.csv"
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"❌ Couldn't find {csv_path}. Please run invoice creation first!")

summary_data = pd.read_csv(csv_path)

# Check required columns
expected_columns = {"InvoiceNumber", "Year", "Month", "DogName", "DaysAttended", "OriginalCostPerDay", "DiscountApplied", "DiscountedCostPerDay", "TotalCost"}
if not expected_columns.issubset(set(summary_data.columns)):
    raise KeyError("❌ 'invoice_summary.csv' missing required columns. Please rebuild invoices properly.")

# === Basic stats ===
total_invoices = len(summary_data)
total_spent = summary_data["TotalCost"].apply(safe_float).sum()
total_days = summary_data["DaysAttended"].sum()

# === Build Structured Invoice Memory ===
structured_invoice_memory = ""
for idx, row in summary_data.iterrows():
    structured_invoice_memory += f"{idx+1}. InvoiceNumber: {row['InvoiceNumber']}, Month: {row['Month']} {row['Year']}, Dog: {row['DogName']}, Days Attended: {row['DaysAttended']}, Total Cost: {row['TotalCost']}\n"

# === Static Context ===
static_context = f"""📚 Background Context:

✅ Important Facts:
- Dog's Name: Snoopy
- Owner: Charlie Brown
- Daycare Location: Pawprints and Playcare LLC
- Snoopy normally attends doggy daycare **every Monday**.
- Occasionally, Snoopy may attend on other days due to unforeseen circumstances or bank holidays.
- Original daycare cost: $22.50/day
- Discounted cost: $11.25/day

📄 Invoice Summary:
There are {total_invoices} invoices covering {total_days} days of daycare.
The total amount paid across all invoices is approximately ${total_spent:,.2f}.

Here are the structured invoice details:
{structured_invoice_memory}
"""

# === Load LLM model ===
llm = OllamaLLM(model="mixtral")

# === Load Vectorstore ===
persist_directory = "chroma_db"
if not os.path.exists(persist_directory):
    raise FileNotFoundError(f"❌ Vectorstore '{persist_directory}' not found. Please run ingestion first.")

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=OllamaEmbeddings(model="mixtral"),
)

# === QA Function ===
def ask_question(user_question):
    # Try answering using CSV memory first
    primary_prompt = (
        f"{static_context}\n\n"
        f"💬 User Question: {user_question}\n\n"
        f"🎯 IMPORTANT: Use the provided background facts (including important facts like day of week), numbers, and structured data first. Trust the background unless the information is missing.\n"
        f"🎯 If the question cannot be answered from background facts or structured data, reply with 'Refer to raw invoice text'."
    )
    primary_response = llm.invoke(primary_prompt)

    # If structured data is not enough, fallback to vector search
    if "Refer to raw invoice text" in primary_response:
        search_results = vectorstore.similarity_search(user_question, k=5)
        search_context = "\n".join([doc.page_content for doc in search_results])

        fallback_prompt = (
            f"📚 Extracts from Invoice Texts:\n{search_context}\n\n"
            f"💬 User Question: {user_question}\n\n"
            f"🎯 Answer using the extracts above."
        )
        final_response = llm.invoke(fallback_prompt)
        return final_response
    else:
        return primary_response

# === Launch Gradio UI ===
gr.Interface(
    fn=ask_question,
    inputs=gr.Textbox(lines=2, placeholder="Ask about Snoopy's invoices..."),
    outputs="text",
    title="🐾 Snoopy Doggy Daycare Invoice Q&A",
    description="Ask questions about Snoopy's daycare invoices! Prioritises structured CSV data but can fallback to invoice text if needed.",
    allow_flagging="never",
).launch()

