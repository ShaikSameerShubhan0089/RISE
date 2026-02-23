#!/usr/bin/env python
import pandas as pd
import os

os.chdir(r'c:\Users\S Sameer\Desktop\autism - Copy')

try:
    print("Reading Excel file...")
    df = pd.read_excel('dataset/ECD Data sets.xlsx')
    
    print("\n=== COLUMNS ===")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    print("\n=== SHAPE ===")
    print(df.shape)
    
    print("\n=== FIRST 15 ROWS ===")
    print(df.head(15))
    
    print("\n=== STATISTICAL SUMMARY ===")
    print(df.describe())
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
