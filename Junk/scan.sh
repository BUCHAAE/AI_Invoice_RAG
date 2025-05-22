#!/bin/bash

# Create a reports directory
mkdir -p trivy-reports

# Dependency scan
trivy fs . --format table --output trivy-reports/dependencies.txt

# Secret scan
trivy fs --scanners secret . --format table --output trivy-reports/secrets.txt

# Config scan
trivy config . --format table --output trivy-reports/config.txt

# Notify
echo "✅ Trivy scan completed. Opening reports..."

# Open reports in Mousepad
mousepad trivy-reports/dependencies.txt &
mousepad trivy-reports/secrets.txt &
mousepad trivy-reports/config.txt &
