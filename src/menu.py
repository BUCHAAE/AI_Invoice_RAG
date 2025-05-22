"""
Author: Andrew Buchanan
Date: 26/04/2025

Purpose:
This script presents a simple menu interface that allows the user to:
1. Clean the working environment (delete PDFs, CSVs, vectorstore).
2. Generate new test invoices.
3. Load the system and launch the Q&A UI.
4. Run the entire workflow end-to-end.
It simplifies the user experience for demonstrations and testing.
"""

import os
import shutil
import subprocess

# Test the scanning.
AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
GITHUB_TOKEN = "ghp_2uL6Rk3YPn89HVx4YZQvBEa2bNK4vE4byp0A"


def clean_environment():
    print("🧹 Cleaning environment...")
    folders_to_delete = ["invoices", "chroma_db"]
    files_to_delete = ["invoice_summary.csv", "attendance_detail.csv"]

    for folder in folders_to_delete:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✅ Deleted folder: {folder}")

    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Deleted file: {file}")

    print("✅ Environment cleaned.\n")

def create_test_invoices():
    print("📄 Generating test invoices...")
    os.makedirs("invoices", exist_ok=True)
    subprocess.run(["python", "src/generate_invoices.py"])
    print("✅ Test invoices created.\n")

def load_and_launch():
    print("🚀 Ingesting invoices and launching Q&A UI...")
    subprocess.run(["python", "src/csv_builder.py"])
    subprocess.run(["python", "src/ingest_invoices_hybrid.py"])
    subprocess.run(["python", "src/demo_ui_hybrid.py"])

def run_everything():
    clean_environment()
    create_test_invoices()
    load_and_launch()

def menu():
    while True:
        print("\n=== Snoopy Invoice Demo Menu ===")
        print("1. Clean environment (delete PDFs, CSVs, vectorstore)")
        print("2. Create test invoices")
        print("3. Load and launch")
        print("4. Run everything")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            clean_environment()
        elif choice == "2":
            create_test_invoices()
        elif choice == "3":
            load_and_launch()
        elif choice == "4":
            run_everything()
        elif choice == "5":
            print("👋 Exiting.")
            break
        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    menu()
