#!/usr/bin/env python
import os
import sys

# Write to file immediately
outfile = os.path.join(os.path.dirname(__file__), 'output.txt')
with open(outfile, 'w') as f:
    f.write('Script started\n')
    
    # Try to import csv and process
    try:
        import csv
        f.write('CSV module imported\n')
        
        filepath = os.path.join(os.path.dirname(__file__), 'T1.csv')
        f.write(f'Looking for: {filepath}\n')
        f.write(f'Exists: {os.path.exists(filepath)}\n')
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                f.write(f'Read {len(rows)} rows\n')
                if rows:
                    f.write(f'First row: {rows[0]}\n')
        
        f.write('Script completed\n')
    except Exception as e:
        f.write(f'Error: {str(e)}\n')
        import traceback
        f.write(traceback.format_exc())
