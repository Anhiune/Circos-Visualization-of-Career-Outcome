#!/bin/bash

# Quick reference commands for generating Circos diagram

# Step 1: Generate data files from CSV
python generate_circos_data.py

# Step 2: Navigate to circos directory
cd circos

# Step 3: Run Circos
circos -conf circos.conf

# Step 4: Check output
ls -lh circos.png

# Optional: Generate SVG version too
# Edit circos.conf and change:
#   png = yes
#   svg = yes
# Then re-run: circos -conf circos.conf
