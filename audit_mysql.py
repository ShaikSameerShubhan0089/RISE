
import sqlalchemy
from sqlalchemy import create_engine, text

def audit_mysql():
    url = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            # Query information_schema for accurate table rows
            query = text("""
                SELECT table_name, table_rows 
                FROM information_schema.tables 
                WHERE table_schema = 'autism_cdss'
                AND table_type = 'BASE TABLE'
            """)
            result = conn.execute(query).fetchall()
            
            print(f"{'Table Name':<25} | {'Rows (Approx)':<12}")
            print("-" * 40)
            for name, rows in result:
                print(f"{name:<25} | {rows:<12}")
                
            if len(result) == 0:
                print("No tables found in MySQL database 'autism_cdss'.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_mysql()
