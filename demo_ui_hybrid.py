"""
Author: Andrew Buchanan
Date: 26/04/2025

Purpose:
This script sets up a local Gradio user interface (UI) to allow users 
to ask questions about the invoices. It loads the pre-built vectorstore, 
injects static facts (like service provider and client information), 
and enables retrieval-augmented QA using a local LLM via Ollama.
"""

import os
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
import gradio as gr

# Paths
persist_directory = "chroma_db"
csv_path = "invoice_summary.csv"
attendance_csv_path = "attendance_detail.csv"
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
ollama_model_name = "mixtral"

# Load Vectorstore
print("\n📦 Loading vectorstore from chroma_db...")
embedding = HuggingFaceEmbeddings(model_name=embedding_model_name)
vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding)

# Load CSVs and generate static context
def generate_context():
    print("\n📄 Reading CSV files...")

    if not (os.path.exists(csv_path) and os.path.exists(attendance_csv_path)):
        return "No invoice or attendance data available."

    invoices_df = pd.read_csv(csv_path)
    attendance_df = pd.read_csv(attendance_csv_path)

    total_invoices = len(invoices_df)

    # Extract year from MonthBilledFor
    invoices_df['Year'] = invoices_df['MonthBilledFor'].apply(lambda x: x.split()[1] if isinstance(x, str) and ' ' in x else None)
    years = sorted(invoices_df['Year'].dropna().unique())

    # Total cost per year
    invoices_df['TotalAmountDue'] = pd.to_numeric(invoices_df['TotalAmountDue'], errors='coerce')
    cost_per_year = invoices_df.groupby('Year')['TotalAmountDue'].sum()

    # Attendance by day
    attendance_df['Day'] = attendance_df['Day'].fillna('Unknown')
    attendance_by_day = attendance_df['Day'].value_counts()

    # Static facts
    service_provider_name = invoices_df['ServiceProviderName'].dropna().unique()[0] if not invoices_df['ServiceProviderName'].dropna().empty else "Unknown"
    service_provider_address = invoices_df['ServiceProviderAddress'].dropna().unique()[0] if not invoices_df['ServiceProviderAddress'].dropna().empty else "Unknown"
    client_name = invoices_df['ClientName'].dropna().unique()[0] if not invoices_df['ClientName'].dropna().empty else "Unknown"
    client_address = invoices_df['ClientAddress'].dropna().unique()[0] if not invoices_df['ClientAddress'].dropna().empty else "Unknown"
    dog_name = invoices_df['DogName'].dropna().unique()[0] if not invoices_df['DogName'].dropna().empty else "Unknown"

    # Build context
    context = f"""
Charlie Brown lives at 32 Willow Crescent, Bloomington, MN 55439, USA.
His dog, Snoopy, attends Pawprints and Playcare LLC.
Pawprints and Playcare LLC is located at 7427 Willow Creek Drive, Suite 210, Bloomington, MN 55439, USA.

This data is about {dog_name}'s daycare attendance.

Client Details:
- Client Name: {client_name}
- Client Address: {client_address}
- Dog's Name: {dog_name}

Service Provider Details:
- Name: {service_provider_name}
- Address: {service_provider_address}

Invoice Summary:
- Total number of invoices: {total_invoices}
- Years covered: {', '.join(years)}
- Total billed amount per year:"""

    for year in years:
        total = cost_per_year.get(year, 0)
        context += f"\n  - {year}: ${total:.2f}"

    context += "\n\nAttendance by day of the week:"
    for day, count in attendance_by_day.items():
        context += f"\n  - {day}: {count} attendances"

    return context.strip()

static_context = generate_context()

# Setup LLM and QA Chain
print("\n🧠 Setting up retrieval QA chain...")
llm = OllamaLLM(model=ollama_model_name)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
)

# Query Function
def answer_question(user_query):
    full_query = f"""Use the following additional context:
{static_context}

Question: {user_query}"""
    result = qa_chain.invoke({"query": full_query})
    return result['result']

# Gradio UI
demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(lines=2, placeholder="Ask about Snoopy's invoices..."),
    outputs=gr.Textbox(label="Answer"),
    title="🐾 Snoopy Invoice Q&A (Local AI)",
)

if __name__ == "__main__":
    demo.launch()
