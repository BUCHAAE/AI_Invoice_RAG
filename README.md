# Author Andrew Buchanan
# Date 26/04/2025


# Snoopy AI Invoice Demo

This project demonstrates an AI-powered Q&A system for analysing doggy daycare invoices using a local large language model (LLM) with Ollama and LangChain.

## Features

- Generates realistic test invoices (PDF)
- Extracts structured data into CSVs
- Builds a Chroma vector database with embeddings
- Provides a Q&A interface using local LLM (Mixtral via Ollama)
- Includes a menu system to run specific parts of the demo

## Requirements

- Python 3.11+
- Ollama (running a model like `mixtral`)
- Tesseract OCR
- poppler-utils
- Python packages from `requirements.txt`

## Quick Start


# Set up Python environment
pyenv install 3.11.8
pyenv virtualenv 3.11.8 ai-invoice-env
pyenv activate ai-invoice-env
pip install -r requirements.txt

# Install Ollama and pull model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mixtral

# Launch the menu
python menu.py



## End-to-End Flow Overview

     Invoice Generation

        Python script (generate_invoices.py) programmatically creates realistic PDF invoices for a fictional doggy daycare.

        Each invoice contains structured fields (e.g. client name, address, dates, costs), making them easy to extract and parse.

    # Invoice Processing and CSV Extraction

        csv_builder.py uses pdfplumber to extract structured data from the PDF invoices.

        It generates two CSV files:

            invoice_summary.csv: One row per invoice with metadata (client, costs, discount, etc.).

            attendance_detail.csv: One row per attendance date with the day of the week and invoice reference.

    # Embedding and Vectorstore Creation

        ingest_invoices_hybrid.py loads the invoice_summary.csv, converts each row to a human-readable paragraph of text.

        Text is chunked and embedded using HuggingFace (BAAI/bge-small-en) embeddings.

        Embeddings are stored in a Chroma vector database for semantic search.

    # Local AI Q&A with Ollama

        demo_ui_hybrid.py launches a Gradio interface for interacting with a local large language model (LLM) (e.g. Mixtral via Ollama).

        The app uses LangChain RetrievalQA, which:

            Accepts a user query.

            Augments the query with static context from the CSVs (e.g. total invoices, provider, client info).

            Retrieves relevant text chunks from the vectorstore.

            Feeds both the query and context into the LLM to generate accurate responses.

    # Interactive Demo Launcher

        menu.py gives a simple terminal menu to run different stages:

            Clean environment

            Create test invoices

            Load and launch the app

            Run everything end-to-end


