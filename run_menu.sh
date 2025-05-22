#!/bin/bash
# Author: Andrew Buchanan
# Date: 26/04/2025
#
# Purpose:
# This shell script runs the complete workflow:
# 1. Cleans previous outputs (if any).
# 2. Generates synthetic invoices.
# 3. Builds CSV summaries.
# 4. Ingests the invoices into a vector database.
# 5. Launches the Gradio-based Q&A system for user interaction.

# Display ASCII art of Snoopy
cat << "EOF"

                    .----.
                 _.'__    `.
             .--(#)(##)---/#\
           .' @          /###\
           :         ,   #####
            `-..__.-' _.-\###/
                  `;_:    `"'
                .'"""""`.
               /,  MENU ,\ 
              //         \\
              `-._______.-'
              ___`. | .'___
             (______|______)            
             Andrew Buchanan.
------------------------------------------------

EOF



# Activate the virtual environment if needed
source ~/.pyenv/versions/ai-invoice-env/bin/activate

echo "=== Checking Python Environment ==="
which python3
python3 --version

# Run the Python menu
python menu.py