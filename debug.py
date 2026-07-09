#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Write output to a log file
log_file = os.path.join(os.path.dirname(__file__), 'debug.log')

with open(log_file, 'w', encoding='utf-8') as log:
    log.write("=== Debug Log ===\n")
    log.write(f"Python executable: {sys.executable}\n")
    log.write(f"Python version: {sys.version}\n")
    log.write(f"Working directory: {os.getcwd()}\n\n")
    
    try:
        import pandas as pd
        log.write("✓ pandas imported successfully\n")
        
        # Try to load a CSV file
        filepath = os.path.join(os.path.dirname(__file__), 'T1.csv')
        log.write(f"Loading file: {filepath}\n")
        
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, encoding='utf-8')
            log.write(f"✓ File loaded successfully\n")
            log.write(f"Shape: {df.shape}\n")
            log.write(f"Columns: {list(df.columns)}\n")
            log.write(f"First row: {df.iloc[0].to_dict()}\n")
        else:
            log.write(f"✗ File not found: {filepath}\n")
            
    except Exception as e:
        log.write(f"✗ Error: {str(e)}\n")
        import traceback
        log.write(traceback.format_exc())

print("Debug log written")
