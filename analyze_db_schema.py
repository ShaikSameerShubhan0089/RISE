import os
from sqlalchemy import create_engine, inspect
import pandas as pd
import json

# Connection URL from .env
DATABASE_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"

def analyze_schema():
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        schema_info = {}
        
        # Get all tables
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")
        
        for table in tables:
            print(f"Analyzing table: {table}")
            table_info = {
                "columns": [],
                "primary_key": inspector.get_pk_constraint(table),
                "foreign_keys": inspector.get_foreign_keys(table),
                "indexes": inspector.get_indexes(table)
            }
            
            # Get columns
            columns = inspector.get_columns(table)
            for col in columns:
                # Convert type to string for serialization
                col['type'] = str(col['type'])
                table_info["columns"].append(col)
                
            schema_info[table] = table_info
            
        # Save to JSON for further processing
        with open("db_schema_analysis.json", "w") as f:
            json.dump(schema_info, f, indent=4)
            
        print("Analysis complete. Saved to db_schema_analysis.json")
        
        # Create a human-readable summary
        summary = []
        for table, info in schema_info.items():
            summary.append(f"### Table: {table}\n")
            summary.append("| Column | Type | Nullable | Default | PK | FK |")
            summary.append("| --- | --- | --- | --- | --- | --- |")
            pk_cols = info["primary_key"]["constrained_columns"]
            fk_info = {fk["constrained_columns"][0]: f"{fk['referred_table']}({fk['referred_columns'][0]})" for fk in info["foreign_keys"]}
            
            for col in info["columns"]:
                name = col["name"]
                ctype = col["type"]
                nullable = col["nullable"]
                default = col["default"]
                is_pk = "Yes" if name in pk_cols else ""
                is_fk = fk_info.get(name, "")
                summary.append(f"| {name} | {ctype} | {nullable} | {default} | {is_pk} | {is_fk} |")
            summary.append("\n")
            
        with open("db_schema_summary.md", "w") as f:
            f.write("\n".join(summary))
            
    except Exception as e:
        print(f"Error during schema analysis: {e}")

if __name__ == "__main__":
    analyze_schema()
