""" 
Author: Andrew Buchanan  
Fully working version: dynamic model selection + improved chunking + embedded summaries
"""

import gradio as gr
import os
import pandas as pd
import requests
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# --- Configuration ---
persist_directory = "chroma_db"
invoice_csv = "invoice_summary.csv"
attendance_csv = "attendance_detail.csv"
embedding_model_name = "BAAI/bge-small-en"

# --- Load Data ---
if not os.path.exists(invoice_csv) or not os.path.exists(attendance_csv):
    raise FileNotFoundError("Missing invoice or attendance CSVs.")

invoice_df = pd.read_csv(invoice_csv)
attendance_df = pd.read_csv(attendance_csv)
attendance_df["ParsedDate"] = pd.to_datetime(attendance_df["Date"], format="%d/%m/%Y", errors="coerce")

# --- Prepare Document Content ---
documents = []

# Invoice lines
for _, row in invoice_df.iterrows():
    documents.append(
        f"Invoice Number: {row['InvoiceNumber']}. "
        f"Month: {row['MonthBilledFor']} {row['Year']}. "
        f"Dog: {row['DogName']}. "
        f"Total: ${row['TotalAmountDue']}. "
        f"Discounted Day Rate: ${row['OriginalCostPerDay']} - {row['PercentageDiscount']}% discount."
    )

# Attendance lines
for _, row in attendance_df.iterrows():
    documents.append(f"{row['DogName']} attended on {row['Date']} ({row['Day']}) under invoice {row['InvoiceNumber']}.")

# Calculated summaries
first_date = attendance_df["ParsedDate"].min()
last_date = attendance_df["ParsedDate"].max()
first_day = first_date.strftime("%A")
last_day = last_date.strftime("%A")
total_attendance = attendance_df["ParsedDate"].notna().sum()
monthly_attendance = attendance_df["ParsedDate"].dt.to_period("M").value_counts().sort_index()
avg_cost_per_day = invoice_df["TotalAmountDue"].sum() / total_attendance
attendance_by_day = attendance_df["Day"].fillna("Unknown").value_counts()
most_common_day = attendance_by_day.idxmax()
gaps = attendance_df["ParsedDate"].sort_values().diff().dt.days
max_gap = int(gaps.max())
unique_months = attendance_df["ParsedDate"].dt.to_period("M").nunique()
attendance_years = sorted(attendance_df["ParsedDate"].dt.year.dropna().unique())
total_cost = invoice_df["TotalAmountDue"].sum()
invoice_count = len(invoice_df)

service_address = invoice_df['ServiceProviderAddress'].iloc[0]
client_address = invoice_df['ClientAddress'].iloc[0]

# Combine narrative and summary
documents.insert(0, f"""Snoopy is a cheerful Beagle owned by Charlie Brown. They live together in Bloomington, Minnesota. Charlie Brown and Snoopys full address is: {client_address}
Each week, Snoopy attends doggy daycare at Pawprints & Playcare LLC, a local service offering structured care for dogs.
The facility is open seven days a week and is located on Willow Creek Drive. The full address of Pawprints and Playcare LLC is: {service_address}.
Every month, Pawprints & Playcare invoices Charlie Brown for Snoopy’s visits, applying a 50% loyalty discount.
Snoopy's first attendance was on {first_date.strftime('%d %B %Y')} ({first_day}).
Snoopy's most recent attendance was on {last_date.strftime('%d %B %Y')} ({last_day}).
Total days attended: {total_attendance}.
Average cost per day: ${avg_cost_per_day:.2f}.
Most frequent day: {most_common_day}s.
Longest gap between visits: {max_gap} days.
Total cost across all invoices: ${total_cost:.2f}.
Years attended: {', '.join(str(y) for y in attendance_years)}.
Total invoices: {invoice_count}.
""")

# Monthly breakdown
documents.append("Monthly attendance breakdown:")
for month, count in monthly_attendance.items():
    documents.append(f"- {month.strftime('%B %Y')}: {count} attendances")

# --- Chunking ---
print("✂️ Splitting documents...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_text("\n".join(documents))

# --- Embedding & Vectorstore ---
print("🔢 Creating vectorstore...")
if os.path.exists(persist_directory):
    import shutil
    shutil.rmtree(persist_directory)

embedding = HuggingFaceEmbeddings(model_name=embedding_model_name)
vectorstore = Chroma.from_texts(chunks, embedding=embedding, persist_directory=persist_directory)
print("✅ Vectorstore created.")

# --- Model selection ---
def get_ollama_models():
    try:
        r = requests.get("http://localhost:11434/api/tags")
        r.raise_for_status()
        return sorted([m["name"] for m in r.json().get("models", [])])
    except:
        return ["llama3:instruct", "mistral:instruct", "openchat", "deepseek-coder:6.7b-instruct"]

available_models = get_ollama_models()
selected_model = available_models[0] if available_models else "llama3:instruct"

# --- Prompt and Chain ---
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="You are a helpful assistant answering only based on the context below.\n"
             "Context:{context}\n"
             "Question: {question}\n"
             "Answer:"
)

# --- Q&A Interface ---
def ask_question(model_choice, query, succinct):
    llm = OllamaLLM(model=model_choice)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=False,
    )
    if succinct:
        query = "Answer as succinctly as possible. " + query
    result = qa_chain.invoke({"query": query})
    return f"[Model: {model_choice}]\n{result['result'].strip()}"

gr.Interface(
    fn=ask_question,
    inputs=[
        gr.Dropdown(choices=available_models, value=selected_model, label="Choose Model"),
        gr.Textbox(label="Your question"),
        gr.Checkbox(label="Make answer succinct", value=True)
    ],
    outputs=gr.Textbox(label="Answer"),
    title="Snoopy Invoice Q&A (RAG + Ollama)"
).launch()