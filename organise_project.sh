#!/bin/bash

# Create folders
mkdir -p src tests data .github/workflows

# Move Python files into src/
mv *.py src/ 2>/dev/null

# Move shell scripts to root (already there)
# Leave run_menu.sh and run_all.sh where they are

# Move README and requirements to root (already there)
# Just in case they aren't:
mv README.md requirements.txt ./ 2>/dev/null

# Move PNG/logo assets to root (or you could use an "assets" folder instead)
mv *.png ./ 2>/dev/null

# Create empty __init__.py files for Python packages
touch src/__init__.py tests/__init__.py

# Add a starter CodeQL workflow file (for Python)
cat <<EOF > .github/workflows/codeql.yml
name: "CodeQL"

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
  schedule:
    - cron: '0 0 * * 0'

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: \${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
EOF

echo "Project structure reorganised successfully."