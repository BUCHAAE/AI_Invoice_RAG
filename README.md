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

```bash
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