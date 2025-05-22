
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)


![Logo](/logo.png)

# Snoopy AI Invoice Demo
**Author: Andrew Buchanan**  
**Date: 26/04/2025**

This project demonstrates an AI-powered Q&A system for analysing doggy daycare invoices using a local large language model (LLM) with Ollama and LangChain.

---

## ✨ Features

- Generates realistic test invoices (PDF)
- Extracts structured data into CSVs
- Builds a Chroma vector database with embeddings
- Provides a Q&A interface using local LLM (e.g. Mixtral via Ollama)
- Includes a CLI menu system to run parts or all of the demo

---

## 🛠️ Requirements

- Python 3.11+
- Ollama (running a model like `mixtral`)
- Tesseract OCR
- poppler-utils
- Python packages from `requirements.txt`

---

## ⚡ Quick Start

### 1. Set up Python environment
```bash
pyenv install 3.11.8
pyenv virtualenv 3.11.8 ai-invoice-env
pyenv activate ai-invoice-env
pip install -r requirements.txt
```

### 2. Install Ollama and pull model
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mixtral
```

### 3. Launch the menu
```bash
python src/menu.py
```

---

## 🔄 End-to-End Flow Overview

### 🐾 1. Invoice Generation
`src/generate_invoices.py` creates PDF invoices with structured fields such as client name, address, dates, and costs.

### 📑 2. Invoice Processing and CSV Extraction
`src/csv_builder.py` extracts invoice content into:

- `invoice_summary.csv`: One row per invoice with metadata
- `attendance_detail.csv`: One row per attendance date

### 🧠 3. Embedding and Vectorstore Creation
`src/ingest_invoices_hybrid.py` converts rows into narrative text and embeds it using `sentence-transformers`. The result is stored in a Chroma vector database.

### 💬 4. Local AI Q&A with Ollama
`src/demo_ui_hybrid.py` launches a Gradio UI that:

- Accepts user questions
- Retrieves relevant chunks from the vectorstore
- Uses Ollama + LangChain to generate answers

### 🧪 5. Interactive Launcher
`src/menu.py` provides a terminal menu to:

- Clean the environment
- Create new test invoices
- Build vector DB and launch the app
- Run the whole process in one go

---

## 🧩 System Dependencies

Make sure you have the following installed via your system package manager:

- `poppler-utils` (for PDF parsing)
- `tesseract-ocr` (if using OCR on scanned PDFs)

---

## 📂 Folder Structure

```
.
├── src/                # All Python source files
├── data/               # Optional data directory
├── invoices/           # Generated PDF invoices
├── chroma_db/          # Vector database
├── invoice_summary.csv
├── attendance_detail.csv
├── run_all.sh
├── run_menu.sh
├── requirements.txt
├── README.md
```

---
